import os
import json
import xml.etree.ElementTree as ET
from tkinter import Tk, Label, Button, filedialog

def xml_indent(elem, level=0):
    # Add indentation and newline characters
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for sub_elem in elem:
            xml_indent(sub_elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def get_line_color_from_name(name):
    color_mapping = {
        "Vt": "0",
        "VtVasc": "16711935",
        "Nec": "16776960",
        "PreNec": "65535",
        "Thrmb": "128",
        "Vesl_EP": "255",
        "CNSi": "12632256",
        "NA": "32896"
    }
    return color_mapping.get(name, "0")

def geojson_to_aperio(geojson_file, aperio_file):
    # Read GeoJSON file
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)

    # Create Aperio XML structure
    aperio_root = ET.Element("Annotations", MicronsPerPixel="0.503300")

    # Initialize a counter for generating Region IDs
    region_id_counter = 1

    # Iterate through features in GeoJSON
    for feature in geojson_data['features']:
        geometry_type = feature['geometry']['type']

        # Check if the geometry type is MultiPolygon or Polygon
        if geometry_type == 'MultiPolygon' or geometry_type == 'Polygon':
            name = feature['properties']['classification']['name']
            line_color = get_line_color_from_name(name)

            # Generate a unique numeric ID for the Region
            region_id = str(region_id_counter)
            region_id_counter += 1

            annotation = ET.SubElement(aperio_root, "Annotation", Id=region_id, Name=name, ReadOnly="0", NameReadOnly="0", LineColorReadOnly="0", Incremental="0", Type="4", LineColor=line_color, Visible="1", Selected="0", MarkupImagePath="", MacroName="")

            # Add attributes
            attributes = ET.SubElement(annotation, "Attributes")
            ET.SubElement(attributes, "Attribute", Name="Description", Id="0", Value="")

            # Add regions
            regions = ET.SubElement(annotation, "Regions")
            region_data = feature['geometry']['coordinates'][0] if geometry_type == 'Polygon' else feature['geometry']['coordinates'][0][0]
            region_attributes = {
                'Type': '0',
                'Zoom': '0.182937',
                'Selected': '1',
                'ImageLocation': '',
                'ImageFocus': '-1',
                'LengthMicrons': '5015.4',
                'AreaMicrons': '964349.7',
                'Text': '',
                'NegativeROA': '0',
                'InputRegionId': '0',
                'Analyze': '1',
                'DisplayId': '1'
            }
            region_element = ET.SubElement(regions, "Region", Id=region_id, **region_attributes)

            # Add region attribute headers
            region_attribute_headers = ET.SubElement(regions, "RegionAttributeHeaders")
            attribute_headers = [
                {"Id": "9999", "Name": "Region", "ColumnWidth": "-1"},
                {"Id": "9997", "Name": "Length", "ColumnWidth": "-1"},
                {"Id": "9996", "Name": "Area", "ColumnWidth": "-1"},
                {"Id": "9998", "Name": "Text", "ColumnWidth": "-1"},
                {"Id": "1", "Name": "Description", "ColumnWidth": "-1"}
            ]
            for header in attribute_headers:
                ET.SubElement(region_attribute_headers, "AttributeHeader", **header)

            # Add vertices
            vertices = ET.SubElement(region_element, "Vertices")
            for coord in region_data:
                vertex = ET.SubElement(vertices, "Vertex", X=str(int(coord[0])), Y=str(int(coord[1])), Z="0")

            # Add closing tags
            plots = ET.SubElement(annotation, "Plots")

    # Indent the XML structure
    xml_indent(aperio_root)

    # Create ElementTree object and write to file
    aperio_tree = ET.ElementTree(aperio_root)
    with open(aperio_file, 'wb') as f:
        aperio_tree.write(f)
class GeoJSONToAperioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GeoJSON to Aperio Converter")

        self.geojson_file_label = Label(root, text="Input GeoJSON file:")
        self.geojson_file_label.pack()

        self.geojson_file_button = Button(root, text="Browse", command=self.browse_geojson_file)
        self.geojson_file_button.pack()

        self.xml_file_label = Label(root, text="Output XML location:")
        self.xml_file_label.pack()

        self.xml_file_button = Button(root, text="Browse", command=self.browse_xml_file)
        self.xml_file_button.pack()

        self.convert_button = Button(root, text="Convert", command=self.convert_geojson_to_aperio)
        self.convert_button.pack()

        self.about_button = Button(root, text="About", command=self.show_about_dialog)
        self.about_button.pack()

    def browse_geojson_file(self):
        geojson_file_path = filedialog.askopenfilename(filetypes=[("GeoJSON files", "*.geojson")])
        self.geojson_file_label.config(text=f"Input GeoJSON file: {geojson_file_path}")
        self.geojson_file_path = geojson_file_path

    def browse_xml_file(self):
        xml_file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        self.xml_file_label.config(text=f"Output XML location: {xml_file_path}")
        self.xml_file_path = xml_file_path

    def convert_geojson_to_aperio(self):
        if hasattr(self, 'geojson_file_path') and hasattr(self, 'xml_file_path'):
            geojson_to_aperio(self.geojson_file_path, self.xml_file_path)
            print("Conversion complete!")
        else:
            print("Please select input GeoJSON file and output XML location.")

    def show_about_dialog(self):
        about_message = "GeoJSON to Aperio Converter\nVersion 1.0\n\nThis tool converts GeoJSON annotations to Aperio XML format. made by Shad Arif Mohammed, 28.11.2023, Mannheim/Germany"
        about_dialog = Tk()
        about_dialog.title("About")
        about_label = Label(about_dialog, text=about_message)
        about_label.pack()
        about_dialog.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = GeoJSONToAperioConverterApp(root)
    root.mainloop()
