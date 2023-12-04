from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import utils


def generate_pdf(images, statistics, output_filename):
    # Create a list to store the elements of the PDF document
    elements = []

    # Load the sample style sheet for text formatting
    styles = getSampleStyleSheet()

    # Iterate over the images and corresponding statistics
    for image_index, (image_filename, plot_stats) in enumerate(zip(images, statistics)):
        # Open the image and get its original size
        img = utils.ImageReader(image_filename)
        img_width, img_height = img.getSize()

        # Calculate the aspect ratio to maintain proportions
        aspect_ratio = img_width / float(img_height)

        # Define a maximum width for the image in the PDF
        max_width = 400  # You can adjust this value as needed

        # Calculate the corresponding height to maintain aspect ratio
        img_width = min(img_width, max_width)
        img_height = img_width / aspect_ratio

        # Add the image to the PDF with specified width and height
        image = Image(image_filename, width=img_width, height=img_height)
        elements.append(image)

        # Create a table for the current image's statistics
        table_data = [
            ["Plot Name", "Mean", "Std", "Y Max", "Y Min"]
        ]

        # Iterate over the statistics for the current image
        for stats in plot_stats:
            # Extract the individual statistics for the current plot
            plot_name, mean, std, y_max, y_min = stats

            # Append a new row with the statistics to the table data
            table_data.append([
                plot_name,
                str(mean),
                str(std),
                str(y_max),
                str(y_min)
            ])

        # Create a table for the current image's statistics
        table = Table(table_data)

        # Apply table styles if needed
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), "gray"),
            ("TEXTCOLOR", (0, 0), (-1, 0), "white"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), "white"),
            ("BOX", (0, 0), (-1, -1), 1, "black"),
            ("GRID", (0, 0), (-1, -1), 1, "black"),
        ]))

        # Add the table to the elements
        elements.append(table)

    # Create a PDF document with the elements
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    doc.build(elements)