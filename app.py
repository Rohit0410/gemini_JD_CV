import glob
from tempfile import NamedTemporaryFile
import pandas as pd
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,ServiceContext
import docx2txt
import os
from statistics import mean
import re
# from fastapi import FastAPI, HTTPException
from typing import List
# from flask import Flask, jsonify,request, json
api_key = "AIzaSyCOiUIr-5sqiGvxrEtH29gtcxfF672JFDc"
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro') 
from pathlib import Path
import shutil

# app = Flask(__name__)

def get_file_path_by_name(file_name):
    # file_path = None  # Ensure it's defined
    file_path=None
    for path in glob.glob(f'**/{file_name}', recursive=True):
        print("Checking path:", path)  # Debug: Log paths being checked
        if file_name in path:
            file_path = path
            break
    if file_path is None:
        raise FileNotFoundError(f"File {file_name} not found.")
    filepath = os.path.abspath(file_path)
    return filepath


def JD(uploaded_jd_file):
    global document_JD
    print('------------',uploaded_jd_file)
    # JD_folder_path = r'D:/Rohit/jdcv_score_app/jdcv_score_app/temp1/'
    # uploaded_jd_file=get_file_path_by_name(uploaded_jd_file)
    # print('jd file1',uploaded_jd_file)
    Document_JD=""" """ 
    if uploaded_jd_file is not None:
        try:
            document_JD=SimpleDirectoryReader(input_files=[uploaded_jd_file]).load_data()
            print('lllllllllllllllllllllll',document_JD)
            for i in document_JD:
                Document_JD+=i.text.replace('\n','').replace('\t','').replace('\xa0',' ')
            prompt_prefix_JD="""you are an HR executive. you have this Job Description"""
            prompt_JD=Document_JD
            prompt_suffix_JD =[" get the key skills required for this position"," get me years of experience required for this position. just get the year in numeric"," get me all the details about the experience must the candidate should have for this position"]
            key_skills_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[0]).text.replace('\n','')
            years_experience_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[1]).text.replace('\n','')
            professional_experience_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[2]).text.replace('\n','')
            return key_skills_JD,years_experience_JD,professional_experience_JD
        except Exception as e:
            print(f"Error processing JD: {e}")

def RESUME(folder):
    # folder=r"D:\Rohit\jdcv_score_app\jdcv_score_app\MANUAL DATA\mixed OPPO INDIA"
    print(folder)
    global resume_section
    resume_section={}
    # for i in os.listdir(folder):
    try:
        for i in folder: 
            # if i is not None:
            print('i',i)
            section=[] 
            # # filepath=os.path.join(folder,i)
            # print(i) 
            document_Resume=SimpleDirectoryReader(input_files=[str(i)]).load_data()
            Document_Resume=""""""
            for j in document_Resume: 
                Document_Resume+=j.text.replace('\n','').replace('\t','').replace('\xa0',' ')
            prompt_prefix_Resume="""you are an HR executive. your job is to get some details from this Resume """
            prompt_Resume=Document_Resume
            prompt_suffix_Resume =["get me all the skills of this candidate from the resume","get me the years of experience the candidate have in total like 15 years, 1year.","get me the summary of the professional experiences from the resume"]
            key_skills_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[0]).text.replace('\n','')
            years_experience_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[1]).text.replace('\n','')
            professional_experience_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[2]).text.replace('\n','')
            # print('key skills  ',key_skills_Resume)
            section.append(key_skills_Resume)
            section.append(years_experience_Resume)
            section.append(professional_experience_Resume)
            # resume_section[i]=[str(key_skills_Resume),str(years_experience_Resume),str(professional_experience_Resume)]
            resume_section[i]=section
        return resume_section
    except Exception as e:
        print(f"Error processing RESUME: {e}")
    

def compare(uploaded_jd_file,folder):
    global h
    # if file or folder is not None:
    try:
        print('jd file',uploaded_jd_file)
        jd = JD(uploaded_jd_file)
        print('folder',folder)
        resume = RESUME(folder)
        # print('resume',resume)
        keys=list(resume.keys())
        print('keys',keys)
        h={} 
        for i in keys:
            print(i)
            filename1 = os.path.basename(i)
            y=resume[i]
            
            prompt_skills="""You are an HR Executive tasked with scoring the similarity between the skills required in a job description (JD) and the skills listed on a resume. Below are the skills from both:
            Skills in the JD: {}
            Skills in the Resume: {}
            Calculate the similarity between these two sets of skills and provide the score in percentage form. Ensure the score is expressed as a plain number (e.g., 100, 50, 0) without any additional text like "Similarity Score:" or "%".""".format(jd[0],y[0])
            
            prompt_year="""You are an HR Executive required to evaluate the similarity in years of experience between what is specified in a job description and what is detailed on a resume. The details are as follows:
            Years of experience required in the JD: {}
            Years of experience listed on the Resume: {}
            Calculate the similarity between the two values and provide the score as a plain percentage number (e.g., 10, 0, 19) without using any additional text like "Similarity Score:" or "%".""".format(jd[1],y[1])
            
            prompt_profession="""You are an HR Executive tasked with scoring the similarity of professional experience as described in a job description (JD) and as listed on a resume. Here are the details:
            Professional experience in the JD: {}
            Professional experience on the Resume: {}
            Assess the similarity between the professional experiences listed in the JD and the resume. Provide the similarity score in a plain percentage number (e.g., 25, 10, 0), ensuring you do not include additional text like "Similarity Score:" or "%" next to the number.""".format(jd[2],y[2])
            
            skills_compare=model.generate_content(prompt_skills).text.replace('\n','')
            year_compare=model.generate_content(prompt_year).text.replace('\n','')
            profession_compare=model.generate_content(prompt_profession).text.replace('\n','')

            match1 = re.search(r'\d+', skills_compare)
            match2 = re.search(r'\d+', year_compare)
            match3 = re.search(r'\d+', profession_compare)

            if match1:
                l1=int(match1.group(0))
            else:
                l1=0
            
            if match2:
                l2=int(match2.group(0))
            else:
                l2=0
            
            if match3:
                l3=int(match3.group(0))
            else:
                l3=0
            print(l1,l2,l3)

            h[filename1]=mean([int(l1),int(l2),int(l3)])
            # h[i]=mean([int(float(skills_compare)),int(float(year_compare)),int(float(profession_compare))])
        h=dict(sorted(h.items(), key=lambda item: item[1], reverse=True))
        print(h)
        return h
    except Exception as e:
        print(f"Error processing COMPARE: {e}")

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def debug_app():
    st.markdown('''# TalentMatch360 🌟''')
    st.markdown('''### Nextgen tool for evaluating Job Descriptions and Resumes''')

    left_column,center_column, right_column = st.columns(3)
    # left_column = st.columns(1)
    # global filepath_jd
    with left_column: 
        file_path=""
        JD_folder_path = r'D:/Rohit/jdcv_score_app/jdcv_score_app/temp3/'
        clear_folder(JD_folder_path)
        uploaded_jd_file = st.file_uploader("Upload your JD here", accept_multiple_files=False)
        print('.................',uploaded_jd_file)
        filepath_jd=''
        os.makedirs(JD_folder_path,exist_ok=True)
        print('done')
        if uploaded_jd_file is not None:
            try:
                # JD_embedding = jd_embedding(folder_jd+uploaded_jd_file.name)
                # JD_folder_path = r'D:/Rohit/jdcv_score_app/jdcv_score_app/temp3/'
                # os.makedirs(JD_folder_path,exist_ok=True)
                # print('done')
                file_path = os.path.join(JD_folder_path, uploaded_jd_file.name)
                print('FILE',file_path)
                with open(file_path, "wb") as f:
                    f.write(uploaded_jd_file.getbuffer())
                # st.success(f"Saved file to {file_path}")
                filepath_jd=uploaded_jd_file.name
                print('u',filepath_jd)
                # Document_JD = JD(tmp_filename)
                # print('0000000000',Document_JD)
                st.write("JD uploaded")
            except Exception as e:
                st.error(f"Error processing jd: {e}")
                st.write("can't uploaded the jd")

    with right_column:
        not_uploaded=""""""
        RESUME_folder_path = r'D:/Rohit/jdcv_score_app/jdcv_score_app/temp4/'
        os.makedirs(RESUME_folder_path,exist_ok=True)

        uploaded_resume_files = st.file_uploader(
            "Upload all of the resumes", accept_multiple_files=True)
        print('kkkkkkk',len(uploaded_resume_files))
        
        print('done')
        resume_embeddings = []  # Dictionary to store resume embeddings
        not_uploaded=[]
        for i in uploaded_resume_files:
            
            if i is not None:
                try:
                    file_path = os.path.join(RESUME_folder_path, i.name)
                    print('FILE',file_path)
                    with open(file_path, "wb") as f:  
                        f.write(i.getbuffer()) 
                        resume_embeddings.append(file_path)
                        print('ttt',resume_embeddings)
                    
                except Exception as e:
                    st.error(f"Error processing resume: {e}")
                    st.write(i,"can't uploaded the resume")
                    not_uploaded.append(i)
        upload = len(uploaded_resume_files)-len(not_uploaded)
        st.write("out of {} Resume, {} were uploaded successfully".format(len(uploaded_resume_files),upload))
        

    with center_column:
        try:
            score=""""""
            # score_dict = {}
            # for filename, resume_embedding in resume_embeddings:
            print('file',filepath_jd)
            print('resEM',resume_embeddings)
            score = compare(file_path,resume_embeddings)
            # score_dict[filename] = score
                # 
            # sorted_dict_desc = dict(sorted(score_dict.items(), key=lambda item: item[1], reverse=True))
            # print('sort',score_dict)
            df = pd.DataFrame(list(score.items()), columns=['Resume', 'Score'])
            st.dataframe(df, use_container_width=True, width=1200,hide_index=True)
            # for i in os.listdir(RESUME_folder_path):
            #     myfile=os.path.join(RESUME_folder_path,i)
            #     if os.path.isfile(myfile):
            #         os.remove(myfile)
                # else:
                #     # If it fails, inform the user.
                #     print("Error: %s file not found" % myfile)
        except Exception as e:
            print(f"Error processing JD: {e}")


if __name__ == '__main__':
    debug_app()



# # compare(r"D:\Rohit\drive-download-20240320T071743Z-001\Oppo India- Chief Financial Officer\mixed\jd4.docx",r"D:\Rohit\jdcv_score_app\jdcv_score_app\MANUAL DATA\mixed OPPO INDIA")

# import glob
# from tempfile import NamedTemporaryFile
# import pandas as pd
# import streamlit as st
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
# import docx2txt
# import os
# from statistics import mean
# import re
# from fastapi import FastAPI, HTTPException
# from typing import List
# from flask import Flask, jsonify, request, json
# api_key = "AIzaSyCOiUIr-5sqiGvxrEtH29gtcxfF672JFDc"
# import google.generativeai as genai
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel('gemini-pro') 
# from pathlib import Path

# # app = Flask(__name__)
# def get_file_path_by_name(file_name):
#     file_path = None  # Ensure it's defined
#     for path in glob.glob(f'**/{file_name}', recursive=True):
#         print("Checking path:", path)  # Debug: Log paths being checked
#         if file_name in path:
#             file_path = path
#             break
#     if file_path is None:
#         raise FileNotFoundError(f"File {file_name} not found.")
#     filepath = os.path.abspath(file_path)
#     return filepath

# def JD(uploaded_jd_file):
#     global document_JD
#     # ... rest of your JD processing logic using uploaded_jd_file.name
#     print('------------',uploaded_jd_file)
#     filepath = get_file_path_by_name(uploaded_jd_file)
#     print('filepath',filepath)
#     Document_JD=""" """ 
#     if uploaded_jd_file is not None:
#             try:
#                 document_JD=SimpleDirectoryReader(input_files=[uploaded_jd_file]).load_data()
#                 print('lllllllllllllllllllllll',document_JD)
#                 for i in document_JD:
#                     Document_JD+=i.text.replace('\n','').replace('\t','').replace('\xa0',' ')
#                 prompt_prefix_JD="""you are an HR executive. you have this Job Description"""
#                 prompt_JD=Document_JD
#                 prompt_suffix_JD =["get the key skills required for this position","get me years of experience required for this position. just get the year in numeric","get me all the details about the experience must the candidate should have for this position"]
#                 key_skills_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[0]).text.replace('\n','')
#                 years_experience_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[1]).text.replace('\n','')
#                 professional_experience_JD=model.generate_content(prompt_prefix_JD+prompt_JD+prompt_suffix_JD[2]).text.replace('\n','')
#                 return key_skills_JD,years_experience_JD,professional_experience_JD
#             except Exception as e:
#                 print(f"Error processing JD: {e}")


# def RESUME(folder):
#     # ... rest of your RESUME processing logic
#     print(folder)
#     global resume_section
#     resume_section={}
#     # for i in os.listdir(folder):
#     try:
#         for i in folder:
#             print('i',i)
#             section=[]  
#             document_Resume=SimpleDirectoryReader(input_files=[str(i)]).load_data()
#             Document_Resume=""""""
#             for j in document_Resume: 
#                 Document_Resume+=j.text.replace('\n','').replace('\t','').replace('\xa0',' ')
#             prompt_prefix_Resume="""you are an HR executive. your job is to get some details from this Resume """
#             prompt_Resume=Document_Resume
#             prompt_suffix_Resume =["get me all the skills of this candidate from the resume","get me the years of experience the candidate have in total like 15 years, 1year.","get me the summary of the professional experiences from the resume"]
#             key_skills_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[0]).text.replace('\n','')
#             years_experience_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[1]).text.replace('\n','')
#             professional_experience_Resume=model.generate_content(prompt_prefix_Resume+prompt_Resume+prompt_suffix_Resume[2]).text.replace('\n','')
#             # print('key skills  ',key_skills_Resume)
#             section.append(key_skills_Resume)
#             section.append(years_experience_Resume)
#             section.append(professional_experience_Resume)
#             # resume_section[i]=[str(key_skills_Resume),str(years_experience_Resume),str(professional_experience_Resume)]
#             resume_section[i]=section
#         return resume_section
#     except Exception as e:
#         print(f"Error processing JD: {e}")

# def compare(file, folder):
#     # ... rest of your compare logic using uploaded_jd_file.name and entries in resume_embeddings
#     global h
#     # if file or folder is not None:
#     try:
#         print('jd file',file)
#         jd = JD(file)
#         print('folder',folder)
#         resume = RESUME(folder)
#         # print('resume',resume)
#         keys=list(resume.keys())
#         print('keys',keys)
#         h={} 
#         for i in keys:
#             print(i)
#             filename1 = os.path.basename(i)
#             y=resume[i]
            
#             prompt_skills="""You are an HR Executive tasked with scoring the similarity between the skills required in a job description (JD) and the skills listed on a resume. Below are the skills from both:
#             Skills in the JD: {}
#             Skills in the Resume: {}
#             Calculate the similarity between these two sets of skills and provide the score in percentage form. Ensure the score is expressed as a plain number (e.g., 100, 50, 0) without any additional text like "Similarity Score:" or "%".""".format(jd[0],y[0])
            
#             prompt_year="""You are an HR Executive required to evaluate the similarity in years of experience between what is specified in a job description and what is detailed on a resume. The details are as follows:
#             Years of experience required in the JD: {}
#             Years of experience listed on the Resume: {}
#             Calculate the similarity between the two values and provide the score as a plain percentage number (e.g., 10, 0, 19) without using any additional text like "Similarity Score:" or "%".""".format(jd[1],y[1])
            
#             prompt_profession="""You are an HR Executive tasked with scoring the similarity of professional experience as described in a job description (JD) and as listed on a resume. Here are the details:
#             Professional experience in the JD: {}
#             Professional experience on the Resume: {}
#             Assess the similarity between the professional experiences listed in the JD and the resume. Provide the similarity score in a plain percentage number (e.g., 25, 10, 0), ensuring you do not include additional text like "Similarity Score:" or "%" next to the number.""".format(jd[2],y[2])
            
#             skills_compare=model.generate_content(prompt_skills).text.replace('\n','')
#             year_compare=model.generate_content(prompt_year).text.replace('\n','')
#             profession_compare=model.generate_content(prompt_profession).text.replace('\n','')

#             match1 = re.search(r'\d+', skills_compare)
#             match2 = re.search(r'\d+', year_compare)
#             match3 = re.search(r'\d+', profession_compare)

#             if match1:
#                 l1=int(match1.group(0))
#             else:
#                 l1=0
            
#             if match2:
#                 l2=int(match2.group(0))
#             else:
#                 l2=0
            
#             if match3:
#                 l3=int(match3.group(0))
#             else:
#                 l3=0
#             print(l1,l2,l3)

#             h[filename1]=mean([int(l1),int(l2),int(l3)])
#             # h[i]=mean([int(float(skills_compare)),int(float(year_compare)),int(float(profession_compare))])
#         h=dict(sorted(h.items(), key=lambda item: item[1], reverse=True))
#         print(h)
#         return h
#     except Exception as e:
#         print(f"Error processing JD: {e}")

# def debug_app():
#     st.markdown('''# TalentMatch360 🌟''')
#     st.markdown('''### Nextgen tool for evaluating Job Descriptions and Resumes''')

#     left_column, center_column, right_column = st.columns(3)
#     # left_column = st.columns(1)
#     # global filepath_jd
#     with left_column:
#         filepath_jd=""
#         uploaded_jd_file = st.file_uploader("Upload your JD here")
#         if uploaded_jd_file is not None:
#             filepath_jd = uploaded_jd_file.name
#         # ... (rest of JD upload logic using uploaded_jd_file.name)

#     with right_column:
#         score = ""
#         uploaded_resume_files = st.file_uploader(
#             "Upload all of the resumes", accept_multiple_files=True)
#         resume_embeddings = []  # List to store uploaded resume paths
#         not_uploaded = []
#         for i in uploaded_resume_files:
#             if i is not None:
#                 try:
#                     resume_embeddings.append(i.name)
#                 except Exception as e:
#                     st.error(f"Error processing resume: {e}")
#                     st.write(i, "can't uploaded the resume")
#                     not_uploaded.append(i)
#         upload = len(uploaded_resume_files) - len(not_uploaded)
#         st.write("out of {} Resume, {} were uploaded successfully".format(len(uploaded_resume_files), upload))

#     with center_column:
#         try:
#             score = compare(filepath_jd, resume_embeddings)
#             df = pd.DataFrame(list(score.items()), columns=['Resume', 'Score'])
#             st.dataframe(df, use_container_width=True, width=1200,hide_index=True)
#             # ... (rest of displaying results logic using score)
#         except Exception as e:
#             print(f"Error processing JD: {e}")

# if __name__ == '__main__':
#     debug_app()
