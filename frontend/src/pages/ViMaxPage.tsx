import { useState, useRef, useEffect } from 'react'
import { videoAPI } from '../services/api'
import { Button } from '../components/ui/Button'

interface Video {
  id: number
  title: string
  view_url: string
  duration: number | null
  file_size: number
  created_at: string
}

export const ViMaxPage = () => {
  const [isRecording, setIsRecording] = useState(false)
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [videos, setVideos] = useState<Video[]>([])
  const [title, setTitle] = useState('')
  const [recordingTime, setRecordingTime] = useState(0)
  const [stream, setStream] = useState<MediaStream | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const liveVideoRef = useRef<HTMLVideoElement>(null)  // ← Live preview
  const playbackVideoRef = useRef<HTMLVideoElement>(null)  // ← Playback
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Load videos on mount
  useEffect(() => {
    loadVideos()
  }, [])

  // Cleanup stream on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  const loadVideos = async () => {
    try {
      const data = await videoAPI.listVideos()
      setVideos(data)
    } catch (error) {
      console.error('Error loading videos:', error)
    }
  }

  const startRecording = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: true
      })

      setStream(mediaStream)

      // Show live preview
      if (liveVideoRef.current) {
        liveVideoRef.current.srcObject = mediaStream
        liveVideoRef.current.play()
      }

      const mediaRecorder = new MediaRecorder(mediaStream, {
        mimeType: 'video/webm;codecs=vp9,opus'
      })

      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        setRecordedBlob(blob)
        
        // Stop all tracks
        mediaStream.getTracks().forEach(track => track.stop())
        setStream(null)
        
        // Clear live preview
        if (liveVideoRef.current) {
          liveVideoRef.current.srcObject = null
        }
        
        // Show playback
        if (playbackVideoRef.current) {
          playbackVideoRef.current.src = URL.createObjectURL(blob)
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access camera/microphone. Please allow permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const uploadVideo = async () => {
    if (!recordedBlob) return

    setIsUploading(true)

    try {
      // Get pre-signed upload URL
      const timestamp = Date.now()
      const filename = `recording_${timestamp}.webm`
      const uploadData = await videoAPI.getUploadUrl(filename, 'video/webm')

      // Upload to S3
      const success = await videoAPI.uploadToS3(uploadData.upload_url, recordedBlob)

      if (success) {
        // Save metadata
        await videoAPI.saveMetadata({
          title: title || `Recording ${new Date().toLocaleString()}`,
          s3_key: uploadData.s3_key,
          s3_url: uploadData.s3_url,
          duration: recordingTime,
          file_size: recordedBlob.size
        })

        // Reset and reload
        setRecordedBlob(null)
        setTitle('')
        setRecordingTime(0)
        loadVideos()
        
        alert('✅ Video uploaded successfully!')
      } else {
        alert('❌ Upload failed. Please try again.')
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      alert(`❌ Error: ${error.message || 'Upload failed'}`)
    } finally {
      setIsUploading(false)
    }
  }

  const deleteVideo = async (videoId: number) => {
    if (!confirm('Are you sure you want to delete this video?')) return

    try {
      await videoAPI.deleteVideo(videoId)
      loadVideos()
      alert('✅ Video deleted')
    } catch (error) {
      console.error('Delete error:', error)
      alert('❌ Failed to delete video')
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const downloadVideo = (blob: Blob, filename?: string) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `video_${Date.now()}.webm`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-white text-2xl sm:text-3xl font-bold flex items-center gap-3">
          <span>🎥</span> ViMax - Video Recorder
        </h1>
        <p className="text-gray-400 mt-2 text-sm sm:text-base">
          Record videos and store them securely on AWS S3
        </p>
      </div>

      {/* Recording Section */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
        <h2 className="text-white font-bold text-lg mb-4">Record New Video</h2>

        {/* Live Preview During Recording */}
        {isRecording && (
          <div className="mb-4">
            <video
              ref={liveVideoRef}
              autoPlay
              muted
              playsInline
              className="w-full max-w-2xl mx-auto rounded-lg bg-black"
            />
            <p className="text-center text-white mt-2 font-semibold">
              🔴 Recording: {formatTime(recordingTime)}
            </p>
          </div>
        )}

        {/* Recording Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          {!isRecording && !recordedBlob && (
            <Button onClick={startRecording} className="flex-1">
              🎬 Start Recording
            </Button>
          )}

          {isRecording && (
            <Button onClick={stopRecording} className="flex-1 bg-red-600 hover:bg-red-700">
              ⏹️ Stop Recording
            </Button>
          )}

          {recordedBlob && (
            <>
              <Button onClick={() => {
                setRecordedBlob(null)
                setTitle('')
              }} className="flex-1 bg-gray-700">
                🔄 Record Again
              </Button>
              <Button 
                onClick={() => downloadVideo(recordedBlob, title ? `${title}.webm` : undefined)} 
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                💾 Download
              </Button>
              <Button onClick={uploadVideo} disabled={isUploading} className="flex-1 bg-blue-600 hover:bg-blue-700">
                {isUploading ? '⏳ Uploading...' : '☁️ Save to Cloud'}
              </Button>
            </>
          )}
        </div>

        {/* Recorded Video Playback */}
        {recordedBlob && (
          <div className="space-y-4">
            <div>
              <p className="text-white font-semibold mb-2">Preview:</p>
              <video
                ref={playbackVideoRef}
                controls
                playsInline
                className="w-full max-w-2xl mx-auto rounded-lg bg-black"
              />
            </div>

            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter video title (optional)"
              className="w-full bg-gray-900 border border-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:border-purple-500"
            />

            <p className="text-gray-400 text-sm">
              Duration: {formatTime(recordingTime)} | Size: {formatFileSize(recordedBlob.size)}
            </p>
          </div>
        )}
      </div>

      {/* Saved Videos */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h2 className="text-white font-bold text-lg mb-4">Your Videos ({videos.length})</h2>

        {videos.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No videos yet. Start recording!</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {videos.map((video) => (
              <div key={video.id} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <video
                  src={video.view_url}
                  controls
                  playsInline
                  className="w-full rounded-lg bg-black mb-3"
                />

                <h3 className="text-white font-semibold mb-2">{video.title || 'Untitled'}</h3>

                <div className="text-gray-400 text-xs space-y-1 mb-3">
                  <p>📅 {new Date(video.created_at).toLocaleDateString()}</p>
                  {video.duration && <p>⏱️ {formatTime(video.duration)}</p>}
                  <p>💾 {formatFileSize(video.file_size)}</p>
                </div>

                <div className="flex gap-2">
                  <a
                    href={video.view_url}
                    download={`${video.title || 'video'}.webm`}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-sm transition-colors text-center"
                  >
                    💾 Download
                  </a>
                  <button
                    onClick={() => deleteVideo(video.id)}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg text-sm transition-colors"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}