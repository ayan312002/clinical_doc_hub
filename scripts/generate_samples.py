"""Generate synthetic clinical documents for testing."""

import json
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

SAMPLES_DIR = Path(__file__).parent.parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

DISCHARGE_SUMMARY = """
St. Mary's Medical Center
DISCHARGE SUMMARY

Patient: Margaret Thompson
DOB: 03/15/1958 (Age 68)
MRN: MRN-2024-0847
Admission Date: 01/05/2026
Discharge Date: 01/09/2026
Attending Physician: Dr. James Chen, MD

ADMISSION DIAGNOSIS:
1. Acute exacerbation of chronic heart failure (I50.9)
2. Type 2 Diabetes Mellitus (E11.65)
3. Hypertension (I10)

HISTORY OF PRESENT ILLNESS:
Ms. Thompson is a 68-year-old female with a past medical history significant for CHF (EF 35%), type 2 diabetes, and hypertension who presented to the ED with 3 days of progressive dyspnea, lower extremity edema, and weight gain of 8 lbs over the past week. Patient reports she was unable to maintain her usual low-sodium diet during the holiday season.

DISCHARGE MEDICATIONS:
1. Lisinopril 20 mg PO daily
2. Furosemide 40 mg PO daily
3. Metformin 1000 mg PO BID
4. Carvedilol 12.5 mg PO BID
5. Aspirin 81 mg PO daily
6. Spironolactone 25 mg PO daily

ALLERGIES: Penicillin (rash), Sulfa drugs (hives)

LAB VALUES AT DISCHARGE:
- BNP: 850 pg/mL (elevated, was 1200 on admission)
- HbA1c: 8.2% (elevated)
- Creatinine: 1.3 mg/dL (mildly elevated)
- Potassium: 4.8 mEq/L (normal)
- Sodium: 138 mEq/L (normal)
- Hemoglobin: 11.2 g/dL (mildly low)

VITAL SIGNS AT DISCHARGE:
- Blood Pressure: 128/78 mmHg
- Heart Rate: 72 bpm
- Respiratory Rate: 18 breaths/min
- O2 Saturation: 96% on room air
- Weight: 162 lbs (down 6 lbs from admission)

PROCEDURES:
- Echocardiogram (01/06): EF 35%, moderate MR, elevated PASP
- Coronary angiography (01/07): No significant CAD

CONDITION AT DISCHARGE:
Stable. Symptoms improved with IV furosemide and fluid restriction. Patient ambulatory, tolerating regular diet.

FOLLOW-UP:
- Cardiology follow-up in 2 weeks with Dr. Chen
- Primary care in 1 week
- Repeat BNP in 1 week
- Daily weight monitoring
- Low sodium diet reinforcement
- Diabetic education referral

DISPOSITION:
Discharged to home with home health services.
"""

LAB_REPORT = """
Quest Diagnostics
LABORATORY REPORT

Patient: Robert Martinez
DOB: 07/22/1975 (Age 50)
MRN: MRN-2024-1203
Ordering Physician: Dr. Sarah Williams, MD
Collection Date: 01/10/2026

COMPLETE BLOOD COUNT (CBC):
- White Blood Cell Count: 12.5 x10^3/uL (HIGH) [Ref: 4.5-11.0]
- Red Blood Cell Count: 4.8 x10^6/uL (Normal) [Ref: 4.5-5.5]
- Hemoglobin: 14.2 g/dL (Normal) [Ref: 13.5-17.5]
- Hematocrit: 42.1% (Normal) [Ref: 38.3-48.6]
- Platelet Count: 245 x10^3/uL (Normal) [Ref: 150-400]
- Mean Corpuscular Volume: 87.7 fL (Normal) [Ref: 80.0-100.0]

COMPREHENSIVE METABOLIC PANEL (CMP):
- Glucose: 185 mg/dL (HIGH) [Ref: 70-100]
- BUN: 22 mg/dL (Normal) [Ref: 7-20]
- Creatinine: 1.1 mg/dL (Normal) [Ref: 0.7-1.3]
- Sodium: 140 mEq/L (Normal) [Ref: 136-145]
- Potassium: 4.2 mEq/L (Normal) [Ref: 3.5-5.0]
- Chloride: 102 mEq/L (Normal) [Ref: 98-106]
- CO2: 24 mEq/L (Normal) [Ref: 23-29]
- Calcium: 9.5 mg/dL (Normal) [Ref: 8.5-10.5]
- Total Protein: 7.0 g/dL (Normal) [Ref: 6.0-8.3]
- Albumin: 4.0 g/dL (Normal) [Ref: 3.5-5.0]
- Bilirubin Total: 0.8 mg/dL (Normal) [Ref: 0.1-1.2]
- Alkaline Phosphatase: 65 U/L (Normal) [Ref: 44-147]
- AST: 32 U/L (Normal) [Ref: 10-40]
- ALT: 28 U/L (Normal) [Ref: 7-56]

LIPID PANEL:
- Total Cholesterol: 245 mg/dL (HIGH) [Ref: <200]
- LDL Cholesterol: 165 mg/dL (HIGH) [Ref: <100]
- HDL Cholesterol: 38 mg/dL (LOW) [Ref: >40]
- Triglycerides: 210 mg/dL (HIGH) [Ref: <150]

THYROID FUNCTION:
- TSH: 2.8 mIU/L (Normal) [Ref: 0.4-4.0]

HEMOGLOBIN A1c: 8.2% (HIGH) [Ref: <5.7]

CLINICAL SIGNIFICANCE:
Patient shows poorly controlled diabetes (HbA1c 8.2%, elevated fasting glucose), dyslipidemia with elevated LDL and triglycerides, and mild leukocytosis which may indicate early infection or inflammation. Recommend diabetes management optimization and statin therapy consideration.

Reported by: Lab Computer
Verified by: Dr. Michael Torres, MD, Pathologist
Date: 01/10/2026
"""

INTAKE_FORM = """
Valley Health Clinic
PATIENT INTAKE FORM

Date of Visit: 01/12/2026

PATIENT INFORMATION:
First Name: Emily
Last Name: Johnson
Date of Birth: 11/03/1990 (Age 35)
Sex: Female
MRN: MRN-2024-1567
Phone: (555) 234-5678
Email: emily.johnson@email.com
Address: 456 Oak Avenue, Springfield, IL 62704
Insurance: BlueCross BlueShield
Policy Number: BC-9876543

EMERGENCY CONTACT:
Name: David Johnson (Spouse)
Phone: (555) 234-5679

CHIEF COMPLAINT:
Persistent fatigue and headaches for the past 2 weeks

HISTORY OF PRESENT ILLNESS:
Patient reports worsening fatigue over the past 2 weeks, accompanied by daily headaches (mostly frontal, mild to moderate intensity). Denies fever, chills, vision changes, or recent trauma. Reports increased stress at work. Sleep pattern disrupted - averaging 5-6 hours per night.

PAST MEDICAL HISTORY:
1. Migraine without aura (diagnosed 2018)
2. Generalized anxiety disorder (diagnosed 2020)
3. Iron deficiency anemia (resolved 2023)

SURGICAL HISTORY:
- Appendectomy (2015)
- Wisdom teeth extraction (2012)

CURRENT MEDICATIONS:
1. Sumatriptan 50 mg PO as needed for migraines
2. Sertraline 50 mg PO daily
3. Iron supplement 325 mg PO daily
4. Multivitamin 1 tablet PO daily

ALLERGIES:
- Codeine (nausea/vomiting)
- No known food allergies

FAMILY HISTORY:
- Mother: Hypertension, Type 2 Diabetes
- Father: Coronary artery disease (MI at age 62)
- Sister: Asthma
- No family history of cancer

SOCIAL HISTORY:
- Occupation: Marketing Manager
- Tobacco: Never smoker
- Alcohol: Social, 2-3 drinks per week
- Exercise: Walking 3x/week
- Diet: Regular diet, reports high caffeine intake (4-5 cups coffee daily)

REVIEW OF SYSTEMS:
- Constitutional: Fatigue, no fever or weight changes
- HEENT: Headaches (frontal), no vision changes
- Cardiovascular: No chest pain, palpitations
- Respiratory: No shortness of breath
- GI: No nausea, vomiting, or diarrhea
- GU: No dysuria or frequency
- Musculoskeletal: No joint pain
- Neurological: Headaches, no numbness or weakness
- Psychiatric: Anxiety stable on current medication

VITAL SIGNS:
- Blood Pressure: 118/72 mmHg
- Heart Rate: 76 bpm
- Temperature: 98.4°F
- Respiratory Rate: 16 breaths/min
- O2 Saturation: 99%
- Height: 5'6" (167.6 cm)
- Weight: 135 lbs (61.2 kg)
- BMI: 21.8 kg/m²

ASSESSMENT:
1. Fatigue, likely multifactorial (stress, possible iron deficiency recurrence, inadequate sleep)
2. Tension-type headaches vs. migraine progression
3. Generalized anxiety disorder, stable

PLAN:
1. Order CBC with iron studies, TSH, CMP
2. Consider sleep hygiene counseling
3. Continue current medications
4. Follow up in 2 weeks with lab results
5. If headaches worsening, consider neurology referral
"""

PHYSICIAN_NOTES = """
St. Mary's Medical Center
PROGRESS NOTES

Date: 01/08/2026
Patient: Margaret Thompson
MRN: MRN-2024-0847
Attending: Dr. James Chen

SUBJECTIVE:
Patient reports feeling much better today. Dyspnea has improved significantly. She is able to walk to the bathroom without oxygen desaturation. Denies chest pain, palpitations, or syncope. Reports decreased appetite but tolerating clear liquids. Last BM was today, normal. denies nausea or vomiting.

OBJECTIVE:
Vital Signs:
- BP: 132/80 mmHg
- HR: 68 bpm, regular
- RR: 16 breaths/min
- Temp: 98.2°F
- SpO2: 97% on 2L NC
- Weight: 164 lbs (down 4 lbs from yesterday)

General: Alert, oriented x4, in no acute distress
HEENT: PERRL, mucous membranes moist
Neck: No JVD, no thyromegaly
Cardiovascular: RRR, no murmurs, gallops, or rubs
Pulmonary: Decreased crackles at bases, improved from admission
Abdomen: Soft, non-tender, normoactive bowel sounds
Extremities: 1+ pitting edema bilaterally (improved from 3+)

ASSESSMENT/PLAN:
1. CHF exacerbation - improving with diuresis
   - Continue IV furosemide, transition to oral when ready
   - Continue fluid restriction to 1.5L/day
   - Daily weights, I&Os
   - Recheck BNP tomorrow

2. Type 2 Diabetes - glucose trending down
   - Continue home metformin
   - Blood glucose monitoring QID
   - Endocrinology follow-up recommended post-discharge

3. Hypertension - well controlled
   - Continue home antihypertensives

Anticipate discharge tomorrow if current trajectory continues.
Will discuss discharge medications and follow-up plan with patient.
"""

FOLLOWUP_NOTES = """
Valley Health Clinic
FOLLOW-UP VISIT NOTE

Date: 01/24/2026
Patient: Emily Johnson
MRN: MRN-2024-1567
Provider: Dr. Sarah Williams, MD

SUBJECTIVE:
Follow-up from 01/12 visit. Patient returns with lab results. Reports improved energy levels since last visit. Headaches have decreased in frequency (now 2-3 per week vs daily). Started sleep hygiene practices - now averaging 7 hours per night. Reduced coffee to 2 cups daily.

OBJECTIVE:
Vital Signs:
- BP: 115/70 mmHg
- HR: 72 bpm
- Weight: 134 lbs

General: Well-appearing, no acute distress

Lab Results Review:
- CBC: WBC 7.2 (normal), Hgb 12.8 (improved from previous 10.1), Hct 38.2%
- Iron studies: Ferritin 45 ng/mL (improved from 12), TIBC 350 mcg/dL, Iron sat 22%
- TSH: 2.1 mIU/L (normal)
- CMP: All within normal limits
- Glucose: 88 mg/dL (normal)

ASSESSMENT:
1. Iron deficiency anemia - resolved with supplementation. Ferritin improved from 12 to 45.
2. Tension headaches - improved with sleep hygiene and stress management
3. Anxiety disorder - stable on sertraline

PLAN:
1. Discontinue iron supplement (iron stores replete)
2. Continue sertraline 50 mg daily
3. Continue sleep hygiene practices
4. Headache diary recommended
5. Return in 3 months for routine follow-up
6. If headaches worsen or change pattern, call for neurology referral

Patient verbalized understanding. Questions answered.
"""


def create_pdf(text: str, filename: str):
    filepath = SAMPLES_DIR / filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.isupper() and len(line) > 3:
            heading_style = styles["Heading2"]
            story.append(Paragraph(f"<b>{line}</b>", heading_style))
        else:
            story.append(Paragraph(line, styles["Normal"]))

    doc.build(story)
    print(f"Created: {filepath}")


def create_txt(text: str, filename: str):
    filepath = SAMPLES_DIR / filename
    filepath.write_text(text.strip())
    print(f"Created: {filepath}")


def main():
    print("Generating synthetic clinical documents...")
    create_pdf(DISCHARGE_SUMMARY, "discharge_summary_thompson.pdf")
    create_pdf(LAB_REPORT, "lab_report_martinez.pdf")
    create_txt(PHYSICIAN_NOTES, "physician_notes_thompson_day3.txt")
    print("\nNote: INTAKE_FORM and FOLLOWUP_NOTES are also available.")
    print("To create DOCX files, install python-docx and extend this script.")
    print("Done!")


if __name__ == "__main__":
    main()
