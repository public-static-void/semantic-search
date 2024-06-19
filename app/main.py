#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Summary       : Semantic search with Elasticsearch and BERT.

Author        : Vadim Titov
Created       : Tue Jun 18 16:07:07 2024 +0200
Last modified : Wed Jun 19 17:19:27 2024 +0200
"""

import os
import shutil

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from elasticsearch import BadRequestError, ConnectionError, Elasticsearch
from sentence_transformers import SentenceTransformer

load_dotenv()

ES_USER = "elastic"
ES_PASS = os.getenv("ELASTIC_PASSWORD", "changeme")
ES_HOST = "https://es01"
ES_PORT = os.getenv("ES_PORT", "9200")
CERT_DIR = os.getenv("CERT_DIR", "/tmp/")
ES_CERT = CERT_DIR + "ca.crt"

IDX = "all_products"
IDX_MAP = {
    "properties": {
        "ProductID": {"type": "long"},
        "ProductName": {"type": "text"},
        "ProductBrand": {"type": "text"},
        "Gender": {"type": "text"},
        "Price (INR)": {"type": "long"},
        "NumImages": {"type": "long"},
        "Description": {"type": "text"},
        "PrimaryColor": {"type": "text"},
        "DescriptionVector": {
            "type": "dense_vector",
            "dims": 768,
            "index": True,
            "similarity": "l2_norm",
        },
    }
}
DATA_DIR = "./data/"
CSV = DATA_DIR + "products.csv"


def connect() -> Elasticsearch:
    """
    Connect to Elasticsearch.

    Returns
    -------
    Elasticsearch
        Elasticsearch client.

    """
    try:
        es = Elasticsearch(
            hosts=[f"{ES_HOST}:{ES_PORT}"],
            ca_certs=ES_CERT,
            basic_auth=(ES_USER, ES_PASS),
        )
    except ConnectionError as e:
        print("Connection Error:", repr(e))
    if es.ping():
        print(
            "Successfully connected to Elasticsearch cluster"
            f" {es.info().body['cluster_name']}!"
        )
    else:
        print("Couldn't connect to Elasticsearch...")
    return es


def create_index(es: Elasticsearch) -> None:
    """
    Create index in Elasticsearch.

    Parameters
    ----------
    es : Elasticsearch
        Elasticsearch client.

    """
    try:
        es.indices.create(index=IDX, mappings=IDX_MAP)
    except BadRequestError as e:
        print("Something went wrong with indexing", repr(e))


def preprocess(es: Elasticsearch, model: SentenceTransformer) -> None:
    """
    Preprocess data and store it in Elasticsearch.

    Parameters
    ----------
    es : Elasticsearch
        Elasticsearch client.
    model : SentenceTransformer
        SentenceTransformer model.

    """
    df = pd.read_csv(CSV).loc[:99]
    df.fillna("None", inplace=True)
    df["DescriptionVector"] = df["Description"].apply(
        lambda x: model.encode(x)
    )
    records = df.to_dict("records")
    for record in records:
        try:
            es.index(index=IDX, document=record, id=record["ProductID"])
        except BadRequestError as e:
            print("Something went wrong with indexing", repr(e))


def search(
    es: Elasticsearch, model: SentenceTransformer, input_keyword: str
) -> dict:
    """
    Search for input keyword in Elasticsearch.

    Parameters
    ----------
    es : Elasticsearch
        Elasticsearch client.
    model : SentenceTransformer
        SentenceTransformer model.
    input_keyword : str
        Input keyword to search for.

    Returns
    -------
    dict
        Search results.

    """
    vector_of_input_keyword = model.encode(input_keyword)

    query = {
        "field": "DescriptionVector",
        "query_vector": vector_of_input_keyword,
        "k": 10,
        "num_candidates": 500,
    }
    res = es.knn_search(
        index="all_products", knn=query, source=["ProductName", "Description"]
    )
    results = res["hits"]["hits"]

    return results


def main() -> None:
    """Create a Steamlit app that allows to perform semantic search."""
    shutil.copy(CERT_DIR + "ca/ca.crt", CERT_DIR + "ca.crt")
    es = connect()
    create_index(es)
    model = SentenceTransformer("all-mpnet-base-v2")
    preprocess(es, model)

    st.title("Semantic Search with ES and BERT")
    # Input: User enters search query
    search_query = st.text_input("Enter your search query")
    # Button: User triggers the search
    if st.button("Search"):
        if search_query:
            # Perform the search and get results
            results = search(es, model, search_query)
            # Display search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if "_source" in result:
                        try:
                            st.header(f"{result['_source']['ProductName']}")
                        except KeyError as e:
                            print(
                                "Something went wrong writing the header",
                                repr(e),
                            )
                        try:
                            st.write(
                                "Description:"
                                f" {result['_source']['Description']}"
                            )
                        except KeyError as e:
                            print(
                                "Something went wrong writing the description",
                                repr(e),
                            )
                        st.divider()


if __name__ == "__main__":
    main()
