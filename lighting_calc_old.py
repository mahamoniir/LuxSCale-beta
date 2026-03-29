import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
import csv
import json
import datetime
import openai

openai.api_key = "chatgbt"

results_global = []
project_info_global = {}

user_data_file = "all_user_data.json"


luminaire_shapes = {
    "SC highbay": {"shape": "circle", "diameter": 0.464},
    "SC backlight": {"shape": "square", "size": 0.6},
    "SC triproof": {"shape": "rectangle", "width": 1.2, "height": 0.1},
}


define_places = {
    "Room": {"lux": 450, "uniformity": 0.5},
    "Office": {"lux": 450, "uniformity": 0.5},
    "Cafe": {"lux": 450, "uniformity": 0.5},
    "Factory production line": {"lux": 350, "uniformity": 0.5},
    "Factory warehouse": {"lux": 150, "uniformity": 0.5}
}


interior_luminaires = {
    "SC downlight": [9],
    "SC triproof": [36],
    "SC backlight": [36, 48]
}


exterior_luminaires = {
    "SC highbay": [100, 150, 200],
    "SC flood light exterior": [100, 150, 200]
}


led_efficacy = {
    "interior": 110,
    "exterior": [145, 160, 200]
}


beam_angle = 120
maintenance_factor = 0.60



def ask_ai_lux(place):
    prompt = f"What is the recommended average lux level for lighting in a '{place}'?"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a lighting design expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    text = response['choices'][0]['message']['content']
    numbers = [int(s) for s in text.split() if s.isdigit()]
    return numbers[0] if numbers else 300  # Default if AI doesn't give number



def cyclic_quadrilateral_area(a, b, c, d):
    s = (a + b + c + d) / 2
    return np.sqrt((s - a) * (s - b) * (s - c) * (s - d))



def determine_zone(height):
    return "interior" if height < 5 else "exterior"



def determine_luminaire(height):
    if height < 5:
        return [(k, v) for k, v in interior_luminaires.items()]
    else:
        return [("SC highbay", [100, 150]) if height <= 12 else ("SC highbay", [200])]


    
def get_spacing_constraints(zone):
    return (2, 4, 2, 4) if zone == "interior" else (4, 7, 7, 12)



def calculate_spacing(length, width, count, margin=2):
    best_x, best_y = 1, 1
    min_diff = float('inf')
    for x in range(1, count + 1):
        y = (count + x - 1) // x
        spacing_x = (length - 2 * margin) / x
        spacing_y = (width - 2 * margin) / y
        diff = abs(spacing_x - spacing_y)
        if spacing_x > 0 and spacing_y > 0 and diff < min_diff:
            min_diff = diff
            best_x, best_y = x, y
    return best_x, best_y



def calculate_lighting(place, sides, height):
    a, b, c, d = sides
    length = max(a, c)
    width = max(b, d)
    area = cyclic_quadrilateral_area(a, b, c, d)
    zone = determine_zone(height)
    required_lux = define_places[place]["lux"]
    required_uniformity = define_places[place]["uniformity"]
    options = determine_luminaire(height)
    min_x, max_x, min_y, max_y = get_spacing_constraints(zone)
    margin = 3

    results = []
    for lum_name, powers in options:
        for power in powers:
            efficacies = led_efficacy[zone] if isinstance(led_efficacy[zone], list) else [led_efficacy[zone]]
            for efficacy in efficacies:
                lumens = power * efficacy
                total_lumens_needed = (required_lux * area) / maintenance_factor
                num_fixtures = int(total_lumens_needed / lumens) + 1

                best_x, best_y = calculate_spacing(length, width, num_fixtures, margin)
                spacing_x = (length - 2 * margin) / best_x
                spacing_y = (width - 2 * margin) / best_y

                spacing_x = max(min(spacing_x, max_x), min_x)
                spacing_y = max(min(spacing_y, max_y), min_y)

                avg_lux = (num_fixtures * lumens * maintenance_factor) / area
                total_power = num_fixtures * power

                if avg_lux >= required_lux:
                    results.append({
                        "Luminaire": lum_name,
                        "Power (W)": power,
                        "Efficacy (lm/W)": efficacy,
                        "Fixtures": num_fixtures,
                        "Spacing X (m)": round(spacing_x, 2),
                        "Spacing Y (m)": round(spacing_y, 2),
                        "Average Lux": round(avg_lux, 2),
                        "Uniformity": required_uniformity,
                        "Total Power (W)": total_power,
                        "Beam Angle (°)": beam_angle
                    })
    return results, length, width




def draw_lighting_distribution(length, width, luminaire_name, num_x, num_y): #مش هظهرها دلوقتي في البي دي اف لغاية ما اظبطها 
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(0, length)
    ax.set_ylim(0, width)
    ax.set_aspect('equal')
    ax.set_title("Lighting Distribution")

    size_x, size_y = fixture_sizes.get(luminaire_name, (0.5, 0.5))
    margin = 1
    dx = (length - 2 * margin) / num_x
    dy = (width - 2 * margin) / num_y

    for i in range(num_x):
        for j in range(num_y):
            cx = margin + (i + 0.5) * dx
            cy = margin + (j + 0.5) * dy
            ax.add_patch(plt.Rectangle((cx - size_x / 2, cy - size_y / 2), size_x, size_y, color='orange'))

    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Width (m)")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        return tmpfile.name



    
def draw_heatmap(length, width, num_x, num_y):
    heatmap = np.zeros((100, 100))
    for i in range(num_x):
        for j in range(num_y):
            x = int(((i + 0.5) * length / num_x) / length * 100)
            y = int(((j + 0.5) * width / num_y) / width * 100)
            heatmap[y, x] += 1
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(heatmap, cmap='YlOrRd', interpolation='bilinear', extent=[0, length, 0, width], origin='lower')
    ax.set_title("Heatmap")
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Width (m)")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        return tmpfile.name
   
def export_csv(results, project_info):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Info"])
        for key, value in project_info.items():
            writer.writerow([key, value])
        writer.writerow([])
        writer.writerow(results[0].keys())
        for res in results:
            writer.writerow(res.values())
    messagebox.showinfo("Success", "CSV exported successfully!")
    

def export_pdf(results, project_info, length, width): # عاوزة افتكر اظبط ترقيم الاوبشن بكرة  
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=False)
    bg_path = "background.png"
    

    def add_page_with_bg():
        pdf.add_page()
        pdf.image(bg_path, x=0, y=0, w=210, h=297)


    # دي هكتب فيها بيانات العميل
    add_page_with_bg()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 50, "Lighting Design Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_xy(10, 60)
    pdf.set_font("Arial", size=12)
    for label, value in project_info.items():
        pdf.cell(200, 10, f"{label}: {value}", ln=True)

    # دي هتخرج النتايج 

    for res in results:
        add_page_with_bg()
        pdf.set_font("Arial", size=11)
        pdf.set_xy(10, 50)
        for key, val in res.items():
            pdf.cell(0, 10, f"{key}: {val}", ln=True)

            
        # دي هرسم فيها الهيت ماب
        num_x = int(res['Fixtures'] ** 0.5)
        num_y = res['Fixtures'] // num_x
        heatmap_path = draw_heatmap(length, width, num_x, num_y)
        pdf.image(heatmap_path, x=30, y=160, w=100)



   #دي نكتب فيها تكنيكال نوتس براحتنا 
    add_page_with_bg()
    pdf.set_font("Arial", size=12)
    pdf.set_xy(20, 60)
    pdf.multi_cell(0, 10,
        "To avoid electrical instability issues, always use drivers with built-in protections:\n"
        "- Over voltage protection\n"
        "- Over current protection"
    )

    pdf.output(file_path)
    messagebox.showinfo("Success", "PDF exported successfully!")





def save_user_data(project_info, results):
    all_data = load_all_user_data()
    all_data.append({"project_info": project_info, "results": results})
    with open(user_data_file, 'w') as f:
        json.dump(all_data, f, indent=4)

def load_all_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            return json.load(f)
    return []




def export_all_users_to_csv():
    all_data = load_all_user_data()
    if not all_data:
        messagebox.showinfo("No Data", "No user data to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Name", "Client Name", "Client Number", "Company Name",
                         "Luminaire", "Power (W)", "Efficacy (lm/W)", "Fixtures",
                         "Spacing X (m)", "Spacing Y (m)", "Average Lux", "Uniformity", "Total Power (W)", "Beam Angle (°)"])
        for data in all_data:
            proj = data["project_info"]
            for res in data["results"]:
                writer.writerow([
                    proj.get("Project Name", ""),
                    proj.get("Client Name", ""),
                    proj.get("Client Number", ""),
                    proj.get("Company Name", ""),
                    res.get("Luminaire", ""),
                    res.get("Power (W)", ""),
                    res.get("Efficacy (lm/W)", ""),
                    res.get("Fixtures", ""),
                    res.get("Spacing X (m)", ""),
                    res.get("Spacing Y (m)", ""),
                    res.get("Average Lux", ""),
                    res.get("Uniformity", ""),
                    res.get("Total Power (W)", ""),
                    res.get("Beam Angle (°)", "")
                ])
    messagebox.showinfo("Success", "All user data exported to CSV successfully!")





def run_gui():
    global results_global, project_info_global



    def on_calculate():
        try:
            place = place_var.get()
            sides = [float(side_vars[i].get()) for i in range(4)]
            height = float(height_var.get())
            project_info = {label: entries[label].get() for label in labels}
            results, length, width = calculate_lighting(place, sides, height)
            results_global.clear()
            results_global.extend(results)
            project_info_global.clear()
            project_info_global.update(project_info)
            result_box.delete(1.0, tk.END)
            for res in results:
                result_box.insert(tk.END, f"{res}\n\n")
            save_user_data(project_info, results)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))




    def on_export_pdf():
        if results_global:
            sides = [float(side_vars[i].get()) for i in range(4)]
            length = max(sides[0], sides[2])
            width = max(sides[1], sides[3])
            export_pdf(results_global, project_info_global, length, width)




    def on_export_csv():
        if results_global:
            export_csv(results_global, project_info_global)


    root = tk.Tk()
    root.title("Lighting Design App")

    labels = ["Project Name", "Client Name", "Client Number", "Company Name"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=i, column=0, sticky="w")
        entry = tk.Entry(root)
        entry.grid(row=i, column=1)
        entries[label] = entry



    tk.Label(root, text="Place").grid(row=4, column=0, sticky="w")
    place_var = ttk.Combobox(root, values=list(define_places.keys()))
    place_var.grid(row=4, column=1)



    side_labels = ["Side A (m)", "Side B (m)", "Side C (m)", "Side D (m)"]
    side_vars = []
    for i, label in enumerate(side_labels):
        tk.Label(root, text=label).grid(row=5 + i, column=0, sticky="w")
        var = tk.Entry(root)
        var.grid(row=5 + i, column=1)
        side_vars.append(var)



    tk.Label(root, text="Height (m)").grid(row=9, column=0, sticky="w")
    height_var = tk.Entry(root)
    height_var.grid(row=9, column=1)




    tk.Button(root, text="Calculate", command=on_calculate).grid(row=10, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Export to PDF", command=on_export_pdf).grid(row=11, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Export to CSV", command=on_export_csv).grid(row=12, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Export All Users to CSV", command=export_all_users_to_csv).grid(row=13, column=0, columnspan=2, pady=5)

    result_box = tk.Text(root, height=20, width=70)
    result_box.grid(row=0, column=2, rowspan=13, padx=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
 
