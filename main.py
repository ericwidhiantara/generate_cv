import csv
import json
from jinja2 import Template
from xhtml2pdf import pisa
import os

class CVGenerator:
    def __init__(self, data):
        self.data = data
        
        # Safely parse JSON strings into Python objects
        self.data['education'] = self._parse_json(data.get('education', '[]'), 'education')
        self.data['work_experience'] = self._parse_json(data.get('work_experience', '[]'), 'work_experience')
        self.data['massage_skills'] = self._parse_json(data.get('massage_skills', '[]'), 'massage_skills')

    def _parse_json(self, json_str, field_name):
        try:
            parsed_data = json.loads(json_str)
            print(f"Parsed {field_name}: {parsed_data}")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"Error parsing {field_name}: {e}")
            return []

    def generate_html(self, template_path):
        # Read the template
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        # Create Jinja2 template
        template = Template(template_content)

        # Process education data
        for edu in self.data['education']:
            edu['education_start'] = edu.pop('start', 'N/A')
            edu['education_finish'] = edu.pop('finish', 'N/A')
            edu['education_name'] = edu.pop('name', 'N/A')
            edu['education_subject'] = edu.pop('subject', 'N/A')
            edu['education_country'] = edu.pop('country', 'N/A')

        # Process work experience data
        for work in self.data['work_experience']:
            work['work_start'] = work.pop('start', 'N/A')
            work['work_finish'] = work.pop('finish', 'N/A')
            work['work_name'] = work.pop('name', 'N/A')
            work['work_subject'] = work.pop('subject', 'N/A')
            work['work_country'] = work.pop('country', 'N/A')

        # Create a dictionary for massage skills
        massage_skills_dict = {
            'Reflexology': '+' if 'Reflexology' in self.data['massage_skills'] else '',
            'Warm Stone': '+' if 'Warm Stone' in self.data['massage_skills'] else '',
            'Lomi-Lomi': '+' if 'Lomi-Lomi Massage' in self.data['massage_skills'] else '',
            'Shiatsu': '+' if 'Shiatsu Massage' in self.data['massage_skills'] else '',
            'Balinese': '+' if 'Balinese Massage' in self.data['massage_skills'] else '',
            'Aromatherapy': '+' if 'Aromatherapy Massage' in self.data['massage_skills'] else '',
            'Hamam': '+' if 'Hamam' in self.data['massage_skills'] else '',
            'Medical': '+' if 'Medical Massage' in self.data['massage_skills'] else '',
            'Thai': '+' if 'Thai Massage' in self.data['massage_skills'] else '',
            'Manicure': '+' if 'Manicure' in self.data['massage_skills'] else '',
            'Deeptissue': '+' if 'Deeptissue Massage' in self.data['massage_skills'] else '',
            'Facial': '+' if 'Facial' in self.data['massage_skills'] else ''
        }

        # Combine all data for template
        template_data = {
            **self.data,
            'education': self.data['education'],
            'work_experience': self.data['work_experience'],
            'massage_skills': massage_skills_dict
        }

        # Render template with data
        html_content = template.render(**template_data)
        return html_content

    def generate_pdf(self, html_content, output_file="result/CV.pdf"):
        # Create PDF from HTML using xhtml2pdf
        with open(output_file, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            print(f"Error generating PDF: {pisa_status.err}")
        else:
            print(f"PDF saved to {output_file}")

def get_input_from_csv(csv_file):
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)[0]
            print(f"Data read from CSV: {data}")
            return CVGenerator(data)
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
        raise
    except IndexError:
        print(f"CSV file is empty or has no data: {csv_file}")
        raise

def save_html(html_content, output_file="result/CV.html"):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML saved to {output_file}")

if __name__ == "__main__":
    csv_file_path = "cv_data.csv"
    template_path = "template.html"  # Your HTML template file
    
    try:
        # Generate CV
        cv = get_input_from_csv(csv_file_path)
        
        # Generate and save HTML
        html_content = cv.generate_html(template_path)
        save_html(html_content)
        
        # Generate PDF from HTML
        cv.generate_pdf(html_content)
    except Exception as e:
        print(f"An error occurred: {e}")
