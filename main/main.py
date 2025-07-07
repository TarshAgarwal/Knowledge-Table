import os
import requests
import json
from typing import List, Dict, Any

# Define the API base URL - adjust if your Knowledge Table API is running on a different port
API_BASE_URL = "http://localhost:8000/api/v1"

# Define the technology areas for classification
TECH_AREAS = [
    "AI and ML", "Application Infrastructure and Software", "Augmented and Virtual Reality",
    "Blockchain", "Cloud Computing and Virtualization", "Computer Vision", "Cryptology",
    "Cybersecurity", "Data Science", "Digital Forensics", "Enterprise Business Technologies",
    "Hardware, Semiconductors and Embedded", "Human Computer Interaction",
    "Identity Management and Authentication", "Internet of Things", "Location and Presence",
    "Material Science", "Mobility and End Points", "Natural Language Processing",
    "Next Generation Computing", "Operating Systems", "Quantum Technology",
    "Robotics and Automation", "Software Defined Infrastructure", "Unmanned Aerial Vehicles",
    "Wireless and Networking Technologies", "5G and 6G", "API and development",
    "Mobile development", "Website development"
]

def upload_pdf(pdf_path: str) -> str:
    """Upload a PDF document to the Knowledge Table API and return the document ID."""
    filename = os.path.basename(pdf_path)
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (filename, f, 'application/pdf')}
        document_data = {
            'name': filename,
            'author': 'Automated Upload',
            'tag': 'Company Analysis'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/document",
            files=files,
            data={'document': json.dumps(document_data)}
        )
        
        if response.status_code != 201:  # Changed from 200 to 201
            raise Exception(f"Failed to upload document: {response.text}")
        
        return response.json()['id']

def create_table_columns() -> List[Dict[str, Any]]:
    """Create the three classification columns for the table."""
    columns = [
        {
            "id": "is_indian",
            "hidden": False,
            "entityType": "Company",
            "type": "boolean",
            "generate": True,
            "query": "Is this company based in India or of Indian origin?",
            "rules": [
                {
                    "id": "rule1",
                    "type": "format",
                    "value": "Y/N"
                }
            ]
        },
        {
            "id": "is_startup",
            "hidden": False,
            "entityType": "Company",
            "type": "boolean",
            "generate": True,
            "query": "Is this company a startup?",
            "rules": [
                {
                    "id": "rule2",
                    "type": "format",
                    "value": "Y/N"
                }
            ]
        },
        {
            "id": "is_tech",
            "hidden": False,
            "entityType": "Company",
            "type": "boolean",
            "generate": True,
            "query": f"Is this company related to technology, specifically in any of these areas: {', '.join(TECH_AREAS)}?",
            "rules": [
                {
                    "id": "rule3",
                    "type": "format",
                    "value": "Y/N"
                }
            ]
        }
    ]
    return columns

def create_table_rows(document_id: str) -> List[Dict[str, Any]]:
    """Create table rows from the document."""
    # Get document chunks from the API
    response = requests.get(f"{API_BASE_URL}/document/{document_id}/chunks")
    
    if response.status_code != 200:
        raise Exception(f"Failed to get document chunks: {response.text}")
    
    chunks = response.json()
    
    # Extract company names from chunks
    # This is a simplified approach - in a real scenario, you might need 
    # more sophisticated NER to extract company names
    rows = []
    for i, chunk in enumerate(chunks):
        # For this example, we'll assume each line in the chunk contains a company name
        lines = chunk['content'].strip().split('\n')
        for line in lines:
            if line.strip():
                rows.append({
                    "id": f"row_{i}_{len(rows)}",
                    "sourceData": line.strip(),  # The company name
                    "hidden": False,
                    "cells": {}  # Will be filled by the API
                })
    
    return rows

def generate_table_cells(columns: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate the table cells using the Knowledge Table API."""
    # Prepare the request payload
    payload = {
        "columns": columns,
        "rows": rows
    }
    
    # Call the API to generate cells
    response = requests.post(
        f"{API_BASE_URL}/query/generate-cells",
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to generate cells: {response.text}")
    
    return response.json()['cells']

def process_pdf_and_classify_companies(pdf_path: str):
    """Process a PDF containing company names and classify them."""
    try:
        # Step 1: Upload the PDF
        document_id = upload_pdf(pdf_path)
        print(f"Document uploaded successfully with ID: {document_id}")
        
        # Step 2: Create table columns
        columns = create_table_columns()
        print("Table columns created")
        
        # Step 3: Create table rows from document
        rows = create_table_rows(document_id)
        print(f"Created {len(rows)} rows from document")
        
        # Step 4: Generate table cells
        cells = generate_table_cells(columns, rows)
        print(f"Generated {len(cells)} cells")
        
        # Step 5: Format and display results
        results = []
        for row in rows:
            company_name = row['sourceData']
            company_data = {
                "Company": company_name,
                "Is Indian": "N/A",
                "Is Startup": "N/A",
                "Is Tech": "N/A"
            }
            
            # Find cells for this row
            for cell in cells:
                if cell['rowId'] == row['id']:
                    if cell['columnId'] == 'is_indian':
                        company_data["Is Indian"] = cell['answer']
                    elif cell['columnId'] == 'is_startup':
                        company_data["Is Startup"] = cell['answer']
                    elif cell['columnId'] == 'is_tech':
                        company_data["Is Tech"] = cell['answer']
            
            results.append(company_data)
        
        # Print results in a table format
        print("\nCompany Classification Results:")
        print("-" * 80)
        print(f"{'Company':<30} | {'Is Indian':<10} | {'Is Startup':<10} | {'Is Tech':<10}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['Company']:<30} | {result['Is Indian']:<10} | {result['Is Startup']:<10} | {result['Is Tech']:<10}")
        
        # Save results to a JSON file
        with open('company_classification_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\nResults saved to company_classification_results.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Replace with the path to your PDF file containing company names
    pdf_path = r"C:\\Users\\TARSH AGARWAL\\OneDrive\\Desktop\\Knowledge_Graph_Table\\main\\Untitled spreadsheet - Sheet1.pdf"
    process_pdf_and_classify_companies(pdf_path)
