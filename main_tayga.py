import csv
import json
from jinja2 import Template
from xhtml2pdf import pisa
import requests

class CVGenerator:
    def __init__(self, data):
        self.data = data
        
        # Safely parse JSON strings into Python objects
        self.data['education'] = self._parse_json(data.get('education', '[]'), 'education')
        self.data['work_experience'] = self._parse_json(data.get('work_experience', '[]'), 'work_experience')

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


        # Combine all data for template
        template_data = {
            **self.data,
            'education': self.data['education'],
            'work_experience': self.data['work_experience'],
        }

        # Render template with data
        html_content = template.render(**template_data)
        return html_content

    def generate_pdf(self, html_content, name):
        # Format the file name based on the provided name
        formatted_name = name.replace(" ", "_")  # Replace spaces with underscores
        output_file = f"result/CV_1_{formatted_name}.pdf"
        
        # Create PDF from HTML using xhtml2pdf
        with open(output_file, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            print(f"Error generating PDF: {pisa_status.err}")
        else:
            print(f"PDF saved to {output_file}")
            

    def generate_pdf_url(self, html_content, name):
        # Format the file name based on the provided name
        formatted_name = name.replace(" ", "_")  # Replace spaces with underscores
        output_file = f"result/CV_{formatted_name}.pdf"

        # API endpoint for generating PDF
        url = "http://103.172.205.223:5000/generate-html-pdf"

        try:
            # Make a POST request to the API with the HTML content
            response = requests.post(url, data={'html': html_content}, stream=True)
            
            if response.status_code == 200:
                # Save the response content as a PDF file
                with open(output_file, "wb") as pdf_file:
                    pdf_file.write(response.content)
                print(f"PDF saved to {output_file}")
            else:
                print(f"Error generating PDF: HTTP {response.status_code}, {response.text}")
        except requests.RequestException as e:
            print(f"Error making request to the PDF generation service: {e}")

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
    csv_file_path = "cv_data_tayga.csv"
    template_path = "template_tayga.html"  # Your HTML template file
    
    try:
        # Generate CV
        cv = get_input_from_csv(csv_file_path)
        
        # Generate and save HTML
        html_content = cv.generate_html(template_path)
        save_html(html_content)
        
        # Extract the name from the data
        name = cv.data.get("full_name", "Unknown").strip()  # Default to "Unknown" if no name is found
        
        # Generate PDF from HTML
        cv.generate_pdf(html_content, name)
        cv.generate_pdf_url(html_content, name)
        
    
    except Exception as e:
        print(f"An error occurred: {e}")
