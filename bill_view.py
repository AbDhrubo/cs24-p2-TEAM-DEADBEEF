import os
from datetime import datetime, timedelta
from io import BytesIO

from dominate.tags import canvas
from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify, make_response
import pdfkit

from models import Vehicle, Landfill_manager_info, Landfill_info, Sts_info
import requests

bill_view = Blueprint("bill_view", __name__, static_folder="static", template_folder="templates")


@bill_view.route('/<int:landfill_id>', methods=['GET', 'POST'])
def bill_view_dash(landfill_id: int):
    if request.method == 'POST':
        data = request.json
        vehicle_id = data.get('vehicle_id')
        weight = data.get('weight')
        vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
        # distance = data.get('distance')
        # user_id = session['id']
        # landfill_manager = Landfill_managerInfo.query.filter(id=id).first()
        sts = Sts_info.query.filter_by(ward_id=vehicle.ward_id).first()
        landfill = Landfill_info.query.filter_by(landfill_id=landfill_id).first()
        # print(sts)
        sts_lat = sts.latitude
        sts_lon = sts.longitude
        landfill_lat = landfill.latitude
        landfill_lon = landfill.longitude

        #distance between sts and landfill site
        distance = 500.0
        #distance needs to be calculated using google api
        endpoint2_url = url_for('bill_view.calculate_distance', _external=True)
        response = requests.post(endpoint2_url, json={
            'sts_lat': sts_lat,
            'sts_lon': sts_lon,
            'landfill_lat': landfill_lat,
            'landfill_lon': landfill_lon
        })

        print(response.status_code)
        if response.status_code == 200:
            print('a')
            distance_data = response.json()
            distance = distance_data.get('distance')
            distance /= 1000.0
        print(distance)

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(minutes=-30)

        endpoint2_url = url_for('bills.calculate_bill', _external=True)
        a_string = arrival_time.strftime("%Y-%m-%d %H:%M:%S")
        d_string = departure_time.strftime("%Y-%m-%d %H:%M:%S")

        response = requests.post(endpoint2_url, json={
                'vehicle_id': vehicle_id,
                'weight': weight,
                'distance': distance,
                'landfill_id': landfill_id,
                'departure_time': d_string,
                'arrival_time': a_string
            })

        if response.status_code == 201:
            print('gg')
            # return redirect(f"/bill-view/{landfill_id}")
            data = response.json()
            bill_id = data.get('bill_id')
            bill = data.get('bill')
            bill_formatted = "{:.2f}".format(float(bill))
            weight_formatted = "{:.2f}".format(float(weight))
            print(weight_formatted)
            response = make_response(jsonify({"success": "True",
                                              "bill": bill_formatted,
                                              "bill_id": bill_id,
                                              "weight": weight_formatted,
                                              "vehicle_id": vehicle_id,
                                              "timestamp": d_string}), 201)

            return response
            # return render_template('login.html')
        else:
            return render_template('error.html', code=response.status_code)

    if request.method == 'GET':
        return render_template('bill_view.html', landfill_id=landfill_id)


@bill_view.route('/calculate-distance', methods=['POST'])
def calculate_distance():
    # if 18 in session['permissions']:
    if 1:
        data = request.json
        sts_lat = data.get('sts_lat')
        sts_lon = data.get('sts_lon')
        landfill_lat = data.get('landfill_lat')
        landfill_lon = data.get('landfill_lon')

        print(sts_lat)
        print(sts_lon)
        print(landfill_lat)
        print(landfill_lon)

        # Constructing the request URL for the Google Distance Matrix API
        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
        origin = f"{sts_lat},{sts_lon}"
        destination = f"{landfill_lat},{landfill_lon}"
        # api_key= "https://maps.googleapis.com/maps/api/js?key=AIzaSyALQ-4LUr6mNIndbvdCCB_1hZhtQ_LtOUg&libraries=places"
        api_key = "AIzaSyALQ-4LUr6mNIndbvdCCB_1hZhtQ_LtOUg&libraries=places"  # Replace this with your actual API key
        url = f"{base_url}origins={origin}&destinations={destination}&key={api_key}"

        # Sending the request to the Google Distance Matrix API
        response = requests.get(url)
        if response.status_code == 200:
            distance_data = response.json()
            print(distance_data)
            # Extracting the distance from the response
            distance = distance_data['rows'][0]['elements'][0]['distance']['value']  # Distance in meters
            return jsonify({'distance': distance})
        else:
            return jsonify({'error': 'Failed to fetch distance'}), response.status_code

    else:
        return jsonify({'error': 'Insufficient permissions'}), 403


@bill_view.route('/generate-pdf', methods=['GET', 'POST'])
def generate_pdf():
    user_data = []
    if request.method == 'POST':
        # Retrieve user input from the form
        title = request.form.get('title')
        author = request.form.get('author')
        publication_year = request.form.get('publication_year')

        # Validate and store the user input
        if title and author and publication_year:
            user_data.append({
                'title': title,
                'author': author,
                'publication_year': publication_year
            })

    pdf_file = generate_pdf_file()
    return send_file(pdf_file, as_attachment=True, download_name='book_catalog.pdf')


def generate_pdf_file():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Create a PDF document
    p.drawString(100, 750, "Book Catalog")

    y = 700
    # for book in user_data:
    #     p.drawString(100, y, f"Title: {book['title']}")
    #     p.drawString(100, y - 20, f"Author: {book['author']}")
    #     p.drawString(100, y - 40, f"Year: {book['publication_year']}")
    #     y -= 60

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


# @bill_view.route('/generate-pdf', methods=['POST'])
# def generate_pdf():
#     data = request.json
#     bill_id = data.get('bill_id')
#     weight = data.get('weight')
#     vehicle_id = data.get('vehicle_id')
#     timestamp = data.get('timestamp')
#     # sts = Sts_info.query.filter_by(ward_id=ward_id).first()
#     # vehicle_match = Vehicle.query.filter_by(id=vehicle_id).first()
#     res = render_template('pdf_template.html', bill_id=bill_id, vehicle_id=vehicle_id, ward_id=ward_id, timestamp=timestamp, weight=weight)
#     response_string = pdfkit.from_string(res, False)
#     response = make_response(response_string, False)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['content-Disposition'] = 'inline;filename=bill.pdf'
#     return response
#     html = (f"<html><body><h3>Bill token</h3><h5>Bill no :#{bill_id}</h5><br>"
#             f"<h5>Vehicle ID :#{vehicle_id}</h5><br>"
#             f"<h5>Ward_ID :#{ward_id}</h5><br>"
#             f"<h5>Weight: :#{weight}</h5><br>"
#             f"<h5>Timestamp :#{timestamp}</h5><br></body></html>")
#     pdf = pdfkit.from_string(html, False)
#
#     headers = {
#         'Content-Type': 'application/pdf',
#         'Content-Disposition': f"attachment;filename={name}.pdf"
#     }
#
#     response = Response(pdf, headers=headers)
#     return response

wkhtmltopdf_path = os.path.join(os.getcwd(), 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

# Set configuration using the path to wkhtmltopdf executable
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


@bill_view.route('/new-pdf/<int:bill_id>/<float:bill>/<int:vehicle_id>/<float:weight>/<timestamp>')
def generate_new_pdf(bill_id, bill: float, vehicle_id, weight: float, timestamp):
    # Prepare data
    data = {
        'bill_id': bill_id,
        'bill': bill,
        'vehicle_id': vehicle_id,
        'weight': weight,
        'timestamp': timestamp
    }

    # Render HTML template with data
    rendered_html = render_template('pdf_template.html', data=data)

    # Configure PDF options
    options = {
        # 'page-size': 'A4',
        # 'margin-top': '0.75in',
        # 'margin-right': '0.75in',
        # 'margin-bottom': '0.75in',
        # 'margin-left': '0.75in',
        'page-height': '5.99in',
        'page-width': '2.83in'
    }

    # Generate PDF from rendered HTML
    pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)

    # Create response with PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

    return response
