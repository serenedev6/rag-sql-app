# data_processor.py
# SQL data ko RAG ke liye text documents mein convert karta hai

import pandas as pd
from langchain_core.documents import Document
from typing import List


def dataframe_to_documents(
    df: pd.DataFrame,
    table_name: str,
    text_columns: list = None,
    metadata_columns: list = None
) -> List[Document]:
    """
    Pandas DataFrame ko LangChain Documents mein convert karta hai.
    
    Args:
        df: SQL se aaya DataFrame
        table_name: Table ka naam (metadata ke liye)
        text_columns: Yeh columns text content mein jayenge
        metadata_columns: Yeh columns metadata mein jayenge
    
    Returns:
        List of LangChain Document objects
    """
    documents = []

    # Agar text_columns specify nahi kiye toh sab columns use karo
    if text_columns is None:
        text_columns = df.columns.tolist()

    # Agar metadata_columns specify nahi kiye toh pehla column use karo (usually ID)
    if metadata_columns is None:
        metadata_columns = [df.columns[0]] if len(df.columns) > 0 else []

    for index, row in df.iterrows():
        # Text content banao — har column ko readable format mein
        text_parts = []
        for col in text_columns:
            if col in df.columns and pd.notna(row[col]):
                text_parts.append(f"{col}: {row[col]}")
        
        page_content = "\n".join(text_parts)

        # Metadata banao
        metadata = {"table": table_name, "row_index": index}
        for col in metadata_columns:
            if col in df.columns:
                metadata[col] = str(row[col]) if pd.notna(row[col]) else ""

        # Document create karo
        if page_content.strip():  # Empty documents skip karo
            doc = Document(page_content=page_content, metadata=metadata)
            documents.append(doc)

    print(f"✅ {len(documents)} documents banaye '{table_name}' se")
    return documents


def chunk_documents(documents: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    Bade documents ko chhote chunks mein todta hai.
    
    Args:
        documents: List of Documents
        chunk_size: Har chunk mein kitne characters
        chunk_overlap: Chunks ke beech overlap
    
    Returns:
        Chunked documents list
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunked = splitter.split_documents(documents)
    print(f"✅ {len(documents)} documents → {len(chunked)} chunks mein split kiye")
    return chunked


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame ko clean karta hai RAG ke liye.
    """
    # NaN values ko empty string se replace karo
    df = df.fillna("")
    
    # Extra whitespace remove karo string columns se
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
    
    # Duplicate rows remove karo
    original_len = len(df)
    df = df.drop_duplicates()
    if len(df) < original_len:
        print(f"⚠️ {original_len - len(df)} duplicate rows remove kiye")
    
    return df
