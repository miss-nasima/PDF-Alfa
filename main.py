from flask import Flask, render_template, request, send_file
from pypdf import PdfReader, PdfWriter
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/tools")
def tools():
    return render_template("tools.html")

# =========================
# PDF MERGER PAGE
# =========================

@app.route("/merger")
def merger():

    return render_template("merger.html")


# =========================
# MERGE PDF
# =========================

@app.route("/merge", methods=["POST"])
def merge_pdfs():

    files = request.files.getlist("pdfs")

    if not files:

        return "No PDF files selected", 400

    writer = PdfWriter()

    temp_files = []

    try:

        for file in files:

            if file.filename == "":
                continue

            temp_name = (
                str(uuid.uuid4())
                + ".pdf"
            )

            temp_path = os.path.join(
                UPLOAD_FOLDER,
                temp_name
            )

            file.save(temp_path)

            temp_files.append(temp_path)

            writer.append(temp_path)

        if not temp_files:

            return (
                "No valid PDF files selected"
            ), 400

        output_path = os.path.join(
            UPLOAD_FOLDER,
            "merged.pdf"
        )

        with open(
            output_path,
            "wb"
        ) as output:

            writer.write(output)

        writer.close()

        return send_file(
            output_path,
            as_attachment=True,
            download_name="merged.pdf"
        )

    except Exception as e:

        try:
            writer.close()
        except:
            pass

        return (
            f"Error while merging PDFs: {str(e)}"
        ), 500


# =========================
# PDF SPLITTER PAGE
# =========================

@app.route("/splitter")
def splitter():

    return render_template("splitter.html")


# =========================
# SPLIT PDF
# =========================

@app.route("/split", methods=["POST"])
def split_pdf():

    file = request.files.get("pdf")

    if not file:

        return "No PDF file selected", 400

    page_range = request.form.get(
        "page_range",
        ""
    ).strip()

    if not page_range:

        return "Please enter page range", 400

    try:

        input_path = os.path.join(
            UPLOAD_FOLDER,
            "split_input.pdf"
        )

        file.save(input_path)

        reader = PdfReader(input_path)

        total_pages = len(reader.pages)

        if "-" in page_range:

            start, end = page_range.split(
                "-",
                1
            )

            start = int(start)

            end = int(end)

        else:

            start = int(page_range)

            end = start

        if (
            start < 1
            or end > total_pages
            or start > end
        ):

            return (
                f"Invalid page range. "
                f"This PDF has {total_pages} pages."
            ), 400

        writer = PdfWriter()

        for page_number in range(
            start - 1,
            end
        ):

            writer.add_page(
                reader.pages[page_number]
            )

        output_path = os.path.join(
            UPLOAD_FOLDER,
            "split_pages.pdf"
        )

        with open(
            output_path,
            "wb"
        ) as output:

            writer.write(output)

        writer.close()

        return send_file(
            output_path,
            as_attachment=True,
            download_name="split_pages.pdf"
        )

    except ValueError:

        return (
            "Invalid page format. "
            "Use example: 2-5 or 3"
        ), 400

    except Exception as e:

        return (
            f"Error while splitting PDF: {str(e)}"
        ), 500


# =========================
# PDF ROTATOR PAGE
# =========================

@app.route("/rotator")
def rotator():

    return render_template("rotator.html")


# =========================
# ROTATE PDF
# =========================

@app.route("/rotate", methods=["POST"])
def rotate_pdf():

    file = request.files.get("pdf")

    if not file:

        return "No PDF file selected", 400

    rotation = request.form.get(
        "rotation",
        "90"
    )

    try:

        rotation = int(rotation)

        if rotation not in [
            90,
            180,
            270
        ]:

            return (
                "Invalid rotation angle"
            ), 400

        input_path = os.path.join(
            UPLOAD_FOLDER,
            "rotate_input.pdf"
        )

        file.save(input_path)

        reader = PdfReader(input_path)

        writer = PdfWriter()

        for page in reader.pages:

            page.rotate(rotation)

            writer.add_page(page)

        output_path = os.path.join(
            UPLOAD_FOLDER,
            "rotated.pdf"
        )

        with open(
            output_path,
            "wb"
        ) as output:

            writer.write(output)

        writer.close()

        return send_file(
            output_path,
            as_attachment=True,
            download_name="rotated.pdf"
        )

    except ValueError:

        return (
            "Invalid rotation value"
        ), 400

    except Exception as e:

        return (
            f"Error while rotating PDF: {str(e)}"
        ), 500


# =========================
# PDF COMPRESSOR PAGE
# =========================

@app.route("/compressor")
def compressor():

    return render_template("compressor.html")


# =========================
# COMPRESS PDF
# =========================

@app.route("/compress", methods=["POST"])
def compress_pdf():

    file = request.files.get("pdf")

    if not file:

        return "No PDF file selected", 400

    try:

        # Save uploaded PDF

        input_path = os.path.join(
            UPLOAD_FOLDER,
            "compress_input.pdf"
        )

        file.save(input_path)


        # Read PDF

        reader = PdfReader(input_path)

        writer = PdfWriter()


        # First add pages to writer

        for page in reader.pages:

            writer.add_page(page)


        # Then compress the pages
        # because they are now part of writer

        for page in writer.pages:

            page.compress_content_streams()


        # Output file

        output_path = os.path.join(
            UPLOAD_FOLDER,
            "compressed.pdf"
        )


        with open(
            output_path,
            "wb"
        ) as output:

            writer.write(output)


        writer.close()


        return send_file(
            output_path,
            as_attachment=True,
            download_name="compressed.pdf"
        )


    except Exception as e:

        return (
            f"Error while compressing PDF: {str(e)}"
        ), 500


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app.run(debug=True)