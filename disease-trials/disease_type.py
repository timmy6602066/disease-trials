# -*- coding: utf-8 -*-
"""Disease_type.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1T7g6JJsRGwvOmq6vjpwlnuD5gQh03I2u
"""

# !pip install groq
# !pip install pymongo

import os
import json
import requests
import pandas as pd
from groq import Groq
from tabulate import tabulate


# Replace with actual patient information
patient_info = {
        'name': 'John Doe',
    'age': 45,
    'gender': 'Male',
    'currentSymptoms': 'fever, cough, fatigue',
    'symptomDuration': '5 days',
    'symptomSeverity': 'moderate',
    'chronicConditions': 'hypertension',
    'pastSurgeries': 'appendectomy',
    'familyHistory': 'diabetes, heart disease',
    'currentMedications': 'lisinopril',
    'previousMedications': 'acetaminophen',
    'allergies': 'penicillin',
    'diagnosis': 'suspected flu'
}



# Replace with your actual Groq API key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)


# Send the request for disease prediction
def predict_disease(patient_info):
    # Construct the initial prompt for disease prediction
    initial_prompt = f"""
    Given the following patient information, what is a possible disease based on the symptoms described?
    Name: {patient_info['name']}
    Age: {patient_info['age']}
    Gender: {patient_info['gender']}
    Current Symptoms: {patient_info['currentSymptoms']}
    Symptom Duration: {patient_info['symptomDuration']}
    Symptom Severity: {patient_info['symptomSeverity']}
    Chronic Conditions: {patient_info['chronicConditions']}
    Past Surgeries: {patient_info['pastSurgeries']}
    Family History: {patient_info['familyHistory']}
    Current Medications: {patient_info['currentMedications']}
    Previous Medications: {patient_info['previousMedications']}
    Allergies: {patient_info['allergies']}
    Diagnosis: {patient_info['diagnosis']}
    """
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Just return the possible disease name based on the symptoms input and patient information."
            },
            {
                "role": "user",
                "content": initial_prompt
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=100,
        temperature=0.7
    )

    # Extract the response text for further processing
    response_text = response.choices[0].message.content.strip()
    print('-------------------', response_text)
    return response_text

#--------------------------------------------------------------------


# Construct the prompt to extract the disease name from the response text
def obtain_disease_name(response_text):
    extraction_prompt = f"""
    Extract the disease name from the following text: "{response_text}"
    """

    # Send the request to extract the disease name
    extraction_response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Extract the exact disease name. No more than 10 words"
            },
            {
                "role": "user",
                "content": extraction_prompt
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=1024,
        temperature=0.7
    )

    # Retrieve the extracted disease name
    disease_name = extraction_response.choices[0].message.content.strip()

    # Print the predicted disease name
    print(f"Predicted disease name: {disease_name}")
    return disease_name


# ------------------------------------------------------------------
def ntc_ids(disease_name):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.titles": disease_name,
        "pageSize": 50
    }

    data_list = []
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        studies = data.get('studies', [])

        for study in studies:
            nctId = study['protocolSection']['identificationModule'].get('nctId', 'Unknown')
            overallStatus = study['protocolSection']['statusModule'].get('overallStatus', 'Unknown')
            startDate = study['protocolSection']['statusModule'].get('startDateStruct', {}).get('date', 'Unknown Date')
            conditions = ', '.join(study['protocolSection']['conditionsModule'].get('conditions', ['No conditions listed']))
            acronym = study['protocolSection']['identificationModule'].get('acronym', 'Unknown')

            interventions_list = study['protocolSection'].get('armsInterventionsModule', {}).get('interventions', [])
            interventions = ', '.join([intervention.get('name', 'No intervention name listed') for intervention in interventions_list]) if interventions_list else "No interventions listed"

            locations_list = study['protocolSection'].get('contactsLocationsModule', {}).get('locations', [])
            locations = ', '.join([f"{location.get('city', 'No City')} - {location.get('country', 'No Country')}" for location in locations_list]) if locations_list else "No locations listed"

            primaryCompletionDate = study['protocolSection']['statusModule'].get('primaryCompletionDateStruct', {}).get('date', 'Unknown Date')
            studyFirstPostDate = study['protocolSection']['statusModule'].get('studyFirstPostDateStruct', {}).get('date', 'Unknown Date')
            lastUpdatePostDate = study['protocolSection']['statusModule'].get('lastUpdatePostDateStruct', {}).get('date', 'Unknown Date')
            studyType = study['protocolSection']['designModule'].get('studyType', 'Unknown')
            phases = ', '.join(study['protocolSection']['designModule'].get('phases', ['Not Available']))

            data_list.append({
                "NCT ID": nctId,
                "Acronym": acronym,
                "Overall Status": overallStatus,
                "Start Date": startDate,
                "Conditions": conditions,
                "Interventions": interventions,
                "Locations": locations,
                "Primary Completion Date": primaryCompletionDate,
                "Study First Post Date": studyFirstPostDate,
                "Last Update Post Date": lastUpdatePostDate,
                "Study Type": studyType,
                "Phases": phases
            })

    df = pd.DataFrame(data_list)
    tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    data_json = df.to_dict(orient='records')
    result_json = json.dumps(data_json, indent=4)
    print('result_json:', result_json)
    result = list()
    for res in json.loads(result_json):
        data = dict()
        for k, v in res.items():
            if k == "NCT ID":
                data['NCT_ID'] = res[k]
            elif k == "Conditions":
                data['Conditions'] = res[k]
            elif k == "Interventions":
                data['Interventions'] = res[k]
            elif k == "Study Type":
                data['Study_Type'] = res[k]
            elif k == "Phases":
                data['Phases'] = res[k]
        result.append(data)
    return result

# print(ntc_ids('flu'))