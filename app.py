import os
import re
import json
import asyncio
from datetime import datetime, timedelta
from nicegui import ui, app
from playwright.async_api import async_playwright

# Data structure extracted from the HTML provided by user
ARXIV_DATA = {
    "grp_physics": {
        "label": "Physics",
        "archives": {
            "astro-ph": {
                "label": "Astrophysics",
                "categories": {
                    "astro-ph.CO": "Cosmology and Nongalactic Astrophysics",
                    "astro-ph.EP": "Earth and Planetary Astrophysics",
                    "astro-ph.GA": "Astrophysics of Galaxies",
                    "astro-ph.HE": "High Energy Astrophysical Phenomena",
                    "astro-ph.IM": "Instrumentation and Methods for Astrophysics",
                    "astro-ph.SR": "Solar and Stellar Astrophysics"
                }
            },
            "cond-mat": {
                "label": "Condensed Matter",
                "categories": {
                    "cond-mat.dis-nn": "Disordered Systems and Neural Networks",
                    "cond-mat.mes-hall": "Mesoscale and Nanoscale Physics",
                    "cond-mat.mtrl-sci": "Materials Science",
                    "cond-mat.other": "Other Condensed Matter",
                    "cond-mat.quant-gas": "Quantum Gases",
                    "cond-mat.soft": "Soft Condensed Matter",
                    "cond-mat.stat-mech": "Statistical Mechanics",
                    "cond-mat.str-el": "Strongly Correlated Electrons",
                    "cond-mat.supr-con": "Superconductivity"
                }
            },
            "gr-qc": {"label": "General Relativity and Quantum Cosmology", "categories": {}},
            "hep-ex": {"label": "High Energy Physics - Experiment", "categories": {}},
            "hep-lat": {"label": "High Energy Physics - Lattice", "categories": {}},
            "hep-ph": {"label": "High Energy Physics - Phenomenology", "categories": {}},
            "hep-th": {"label": "High Energy Physics - Theory", "categories": {}},
            "math-ph": {"label": "Mathematical Physics", "categories": {}},
            "nlin": {
                "label": "Nonlinear Sciences",
                "categories": {
                    "nlin.AO": "Adaptation and Self-Organizing Systems",
                    "nlin.CD": "Chaotic Dynamics",
                    "nlin.CG": "Cellular Automata and Lattice Gases",
                    "nlin.PS": "Pattern Formation and Solitons",
                    "nlin.SI": "Exactly Solvable and Integrable Systems"
                }
            },
            "nucl-ex": {"label": "Nuclear Experiment", "categories": {}},
            "nucl-th": {"label": "Nuclear Theory", "categories": {}},
            "physics": {
                "label": "Physics",
                "categories": {
                    "physics.acc-ph": "Accelerator Physics",
                    "physics.ao-ph": "Atmospheric and Oceanic Physics",
                    "physics.app-ph": "Applied Physics",
                    "physics.atm-clus": "Atomic and Molecular Clusters",
                    "physics.atom-ph": "Atomic Physics",
                    "physics.bio-ph": "Biological Physics",
                    "physics.chem-ph": "Chemical Physics",
                    "physics.class-ph": "Classical Physics",
                    "physics.comp-ph": "Computational Physics",
                    "physics.data-an": "Data Analysis, Statistics and Probability",
                    "physics.ed-ph": "Physics Education",
                    "physics.flu-dyn": "Fluid Dynamics",
                    "physics.gen-ph": "General Physics",
                    "physics.geo-ph": "Geophysics",
                    "physics.hist-ph": "History and Philosophy of Physics",
                    "physics.ins-det": "Instrumentation and Detectors",
                    "physics.med-ph": "Medical Physics",
                    "physics.optics": "Optics",
                    "physics.plasm-ph": "Plasma Physics",
                    "physics.pop-ph": "Popular Physics",
                    "physics.soc-ph": "Physics and Society",
                    "physics.space-ph": "Space Physics"
                }
            },
            "quant-ph": {"label": "Quantum Physics", "categories": {}}
        }
    },
    "grp_math": {
        "label": "Mathematics",
        "archives": {
            "math": {
                "label": "Mathematics",
                "categories": {
                    "math.AC": "Commutative Algebra",
                    "math.AG": "Algebraic Geometry",
                    "math.AP": "Analysis of PDEs",
                    "math.AT": "Algebraic Topology",
                    "math.CA": "Classical Analysis and ODEs",
                    "math.CO": "Combinatorics",
                    "math.CT": "Category Theory",
                    "math.CV": "Complex Variables",
                    "math.DG": "Differential Geometry",
                    "math.DS": "Dynamical Systems",
                    "math.FA": "Functional Analysis",
                    "math.GM": "General Mathematics",
                    "math.GN": "General Topology",
                    "math.GR": "Group Theory",
                    "math.GT": "Geometric Topology",
                    "math.HO": "History and Overview",
                    "math.IT": "Information Theory",
                    "math.KT": "K-Theory and Homology",
                    "math.LO": "Logic",
                    "math.MG": "Metric Geometry",
                    "math.MP": "Mathematical Physics",
                    "math.NA": "Numerical Analysis",
                    "math.NT": "Number Theory",
                    "math.OA": "Operator Algebras",
                    "math.OC": "Optimization and Control",
                    "math.PR": "Probability",
                    "math.QA": "Quantum Algebra",
                    "math.RA": "Rings and Algebras",
                    "math.RT": "Representation Theory",
                    "math.SG": "Symplectic Geometry",
                    "math.SP": "Spectral Theory",
                    "math.ST": "Statistics Theory"
                }
            }
        }
    },
    "grp_cs": {
        "label": "Computer Science",
        "archives": {
            "cs": {
                "label": "Computer Science",
                "categories": {
                    "cs.AI": "Artificial Intelligence",
                    "cs.AR": "Hardware Architecture",
                    "cs.CC": "Computational Complexity",
                    "cs.CE": "Computational Engineering, Finance, and Science",
                    "cs.CG": "Computational Geometry",
                    "cs.CL": "Computation and Language",
                    "cs.CR": "Cryptography and Security",
                    "cs.CV": "Computer Vision and Pattern Recognition",
                    "cs.CY": "Computers and Society",
                    "cs.DB": "Databases",
                    "cs.DC": "Distributed, Parallel, and Cluster Computing",
                    "cs.DL": "Digital Libraries",
                    "cs.DM": "Discrete Mathematics",
                    "cs.DS": "Data Structures and Algorithms",
                    "cs.ET": "Emerging Technologies",
                    "cs.FL": "Formal Languages and Automata Theory",
                    "cs.GL": "General Literature",
                    "cs.GR": "Graphics",
                    "cs.GT": "Computer Science and Game Theory",
                    "cs.HC": "Human-Computer Interaction",
                    "cs.IR": "Information Retrieval",
                    "cs.IT": "Information Theory",
                    "cs.LG": "Machine Learning",
                    "cs.LO": "Logic in Computer Science",
                    "cs.MA": "Multiagent Systems",
                    "cs.MM": "Multimedia",
                    "cs.MS": "Mathematical Software",
                    "cs.NA": "Numerical Analysis",
                    "cs.NE": "Neural and Evolutionary Computing",
                    "cs.NI": "Networking and Internet Architecture",
                    "cs.OH": "Other Computer Science",
                    "cs.OS": "Operating Systems",
                    "cs.PF": "Performance",
                    "cs.PL": "Programming Languages",
                    "cs.RO": "Robotics",
                    "cs.SC": "Symbolic Computation",
                    "cs.SD": "Sound",
                    "cs.SE": "Software Engineering",
                    "cs.SI": "Social and Information Networks",
                    "cs.SY": "Systems and Control"
                }
            }
        }
    },
    "grp_q-bio": {"label": "Quantitative Biology", "archives": {"q-bio": {"label": "Quantitative Biology", "categories": {
        "q-bio.BM": "Biomolecules", "q-bio.CB": "Cell Behavior", "q-bio.GN": "Genomics", "q-bio.MN": "Molecular Networks",
        "q-bio.NC": "Neurons and Cognition", "q-bio.OT": "Other Quantitative Biology", "q-bio.PE": "Populations and Evolution",
        "q-bio.QM": "Quantitative Methods", "q-bio.SC": "Subcellular Processes", "q-bio.TO": "Tissues and Organs"
    }}}},
    "grp_q-fin": {"label": "Quantitative Finance", "archives": {"q-fin": {"label": "Quantitative Finance", "categories": {
        "q-fin.CP": "Computational Finance", "q-fin.EC": "Economics", "q-fin.GN": "General Finance", "q-fin.MF": "Mathematical Finance",
        "q-fin.PM": "Portfolio Management", "q-fin.PR": "Pricing of Securities", "q-fin.RM": "Risk Management",
        "q-fin.ST": "Statistical Finance", "q-fin.TR": "Trading and Market Microstructure"
    }}}},
    "grp_stat": {"label": "Statistics", "archives": {"stat": {"label": "Statistics", "categories": {
        "stat.AP": "Applications", "stat.CO": "Computation", "stat.ME": "Methodology", "stat.ML": "Machine Learning",
        "stat.OT": "Other Statistics", "stat.TH": "Statistics Theory"
    }}}},
    "grp_eess": {"label": "Electrical Engineering and Systems Science", "archives": {"eess": {"label": "Electrical Engineering and Systems Science", "categories": {
        "eess.AS": "Audio and Speech Processing", "eess.IV": "Image and Video Processing", "eess.SP": "Signal Processing", "eess.SY": "Systems and Control"
    }}}},
    "grp_econ": {"label": "Economics", "archives": {"econ": {"label": "Economics", "categories": {
        "econ.EM": "Econometrics", "econ.GN": "General Economics", "econ.TH": "Theoretical Economics"
    }}}},
}

class ArXivDownloader:
    def __init__(self):
        self.results = []
        self.is_loading = False
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    async def fetch_papers(self, subject, start_date, include_abs):
        self.is_loading = True
        ui.notify(f"Fetching papers for {subject} since {start_date}...")
        self.results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="chrome", headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            url = f"https://arxiv.org/catchup?subject={subject}&date={start_date}"
            if include_abs:
                url += "&include_abs=True"
            
            print(f"Navigating to {url}")
            await page.goto(url)
            
            try:
                await page.wait_for_selector("dl", timeout=15000)
            except:
                self.is_loading = False
                ui.notify("No papers found or page timed out.", type="warning")
                await browser.close()
                return

            # Parsing headers and papers
            # We look for H3 (dates) and DT (papers)
            elements = await page.query_selector_all("h2, h3, dl > dt")
            current_date_str = "Recent Submissions"
            
            for el in elements:
                tag = await el.evaluate("el => el.tagName")
                if tag in ["H2", "H3"]:
                    text = await el.inner_text()
                    current_date_str = text.strip()
                    continue
                
                if tag == "DT":
                    pdf_link_el = await el.query_selector('a[title="Download PDF"]')
                    if not pdf_link_el:
                        continue
                    
                    pdf_url = await pdf_link_el.get_attribute("href")
                    if not pdf_url.startswith("http"):
                        pdf_url = "https://arxiv.org" + pdf_url
                    
                    paper_id_el = await el.query_selector('a[id^="pdf-"]')
                    paper_id = await paper_id_el.inner_text() if paper_id_el else "Unknown"
                    
                    dd = await page.evaluate_handle("el => el.nextElementSibling", el)
                    title_el = await dd.query_selector(".list-title")
                    title = await title_el.inner_text() if title_el else "No Title"
                    title = title.replace("Title: ", "").strip()
                    
                    self.results.append({
                        "id": paper_id,
                        "title": title,
                        "pdf_url": pdf_url,
                        "date": current_date_str,
                        "selected": False
                    })
            
            await browser.close()
        
        self.is_loading = False
        if not self.results:
            ui.notify("No papers found for the selected criteria.", type="warning")
        else:
            ui.notify(f"Found {len(self.results)} papers.")

    async def download_papers(self, papers):
        if not papers:
            ui.notify("No papers selected", type="warning")
            return
            
        ui.notify(f"Starting download of {len(papers)} papers...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="chrome", headless=True)
            context = await browser.new_context()
            
            for paper in papers:
                filename = f"{paper['id'].replace(':', '_')}.pdf"
                filepath = os.path.join(self.download_dir, filename)
                
                print(f"Downloading {paper['id']}...")
                try:
                    response = await context.request.get(paper['pdf_url'], timeout=30000)
                    if response.status == 200:
                        with open(filepath, "wb") as f:
                            f.write(await response.body())
                        ui.notify(f"Downloaded {paper['id']}", type="positive")
                    else:
                        ui.notify(f"Failed to download {paper['id']} (Status {response.status})", type="negative")
                except Exception as e:
                    ui.notify(f"Error downloading {paper['id']}: {str(e)}", type="negative")
                
                await asyncio.sleep(0.5)
            
            await browser.close()
        ui.notify("Bulk download completed.")

downloader = ArXivDownloader()

@ui.page('/')
def main_page():
    ui.colors(primary='#1a237e', secondary='#303f9f', accent='#ff4081')
    
    with ui.header().classes('items-center justify-between shadow-md px-6 py-2 bg-indigo-900 text-white'):
        ui.label('ArXiv Catchup Downloader').classes('text-2xl font-bold')
        ui.button(icon='settings', on_click=lambda: ui.notify('Settings not implemented')).props('flat color=white')

    with ui.column().classes('w-full p-8 max-w-5xl mx-auto'):
        # Selection Card
        with ui.card().classes('w-full p-8 shadow-2xl rounded-2xl bg-white'):
            ui.label('Search Criteria').classes('text-2xl font-bold mb-6 text-indigo-900')
            
            with ui.row().classes('w-full gap-6'):
                group_select = ui.select(
                    {k: v['label'] for k, v in ARXIV_DATA.items()},
                    label='Group',
                    on_change=lambda e: update_archives(e.value)
                ).classes('flex-1')
                
                archive_select = ui.select(
                    {},
                    label='Archive',
                    on_change=lambda e: update_categories(group_select.value, e.value)
                ).classes('flex-1')
                
                category_select = ui.select(
                    {},
                    label='Category (Optional)'
                ).classes('flex-1')

            with ui.row().classes('w-full gap-6 items-end mt-8'):
                with ui.column().classes('flex-1'):
                    ui.label('Start Date').classes('text-sm font-medium text-slate-600 mb-1')
                    with ui.input(value='2026-05-13') as start_date:
                        with ui.menu().props('no-parent-event') as menu:
                            ui.date().bind_value(start_date)
                        with start_date.add_slot('append'):
                            ui.icon('calendar_month').on('click', menu.open).classes('cursor-pointer text-indigo-600')

                with ui.column().classes('flex-1'):
                    ui.label('End Date (UI Range)').classes('text-sm font-medium text-slate-600 mb-1')
                    with ui.input(value='2026-05-14') as end_date:
                        with ui.menu().props('no-parent-event') as menu2:
                            ui.date().bind_value(end_date)
                        with end_date.add_slot('append'):
                            ui.icon('calendar_today').on('click', menu2.open).classes('cursor-pointer text-indigo-600')
                
                include_abs = ui.checkbox('Include Abstracts', value=True).classes('mb-2 text-slate-700')
                
                ui.button('Fetch Papers', on_click=lambda: start_fetch()).classes('px-12 h-14 rounded-xl bg-indigo-700 text-white font-bold shadow-lg hover:bg-indigo-800 transition-all')

        # Global Action Bar (always present but buttons only show when results exist)
        action_bar_container = ui.row().classes('w-full mt-10 items-center justify-between p-4 bg-slate-100 rounded-xl shadow-inner')
        action_bar_container.visible = False # Start hidden
        
        with action_bar_container:
            with ui.row().classes('gap-4'):
                ui.button('Select All', on_click=lambda: set_all_selected(True)).props('outline color=indigo').classes('rounded-lg')
                ui.button('Deselect All', on_click=lambda: set_all_selected(False)).props('outline color=grey').classes('rounded-lg')
            
            ui.button('Download Selected', on_click=lambda: download_selected()).classes('bg-green-600 text-white px-8 py-3 rounded-xl font-bold shadow-lg hover:bg-green-700 transition-transform active:scale-95')

        # Results area
        results_container = ui.column().classes('w-full mt-6 gap-6')

    def update_archives(group_id):
        archives = ARXIV_DATA[group_id]['archives']
        archive_select.options = {k: v['label'] for k, v in archives.items()}
        archive_select.value = next(iter(archive_select.options.keys())) if archive_select.options else None
        update_categories(group_id, archive_select.value)

    def update_categories(group_id, archive_id):
        if not archive_id:
            category_select.options = {}
            category_select.value = None
            return
        categories = ARXIV_DATA[group_id]['archives'][archive_id]['categories']
        category_select.options = categories
        category_select.value = None

    async def start_fetch():
        subject = category_select.value or archive_select.value or group_select.value
        if not subject:
            ui.notify("Please select at least a Group and Archive", type="negative")
            return
        
        await downloader.fetch_papers(subject, start_date.value, include_abs.value)
        refresh_results()

    def set_all_selected(value):
        for paper in downloader.results:
            paper['selected'] = value
        refresh_results()

    async def download_selected():
        selected = [p for p in downloader.results if p['selected']]
        if not selected:
            ui.notify("No papers selected", type="warning")
            return
        await downloader.download_papers(selected)

    def refresh_results():
        results_container.clear()
        if not downloader.results:
            action_bar_container.visible = False
            return
        
        action_bar_container.visible = True
        
        # Group results by date for better UI
        by_date = {}
        for paper in downloader.results:
            d = paper['date']
            if d not in by_date:
                by_date[d] = []
            by_date[d].append(paper)

        with results_container:
            for date_str, papers in by_date.items():
                with ui.column().classes('w-full'):
                    ui.label(date_str).classes('text-xl font-extrabold text-indigo-900 mt-6 border-b-4 border-indigo-200 w-full pb-2 px-2')
                    for paper in papers:
                        with ui.card().classes('w-full p-5 hover:shadow-xl transition-all border-l-8 border-indigo-400 bg-white rounded-lg'):
                            with ui.row().classes('w-full items-center gap-6 no-wrap'):
                                ui.checkbox().bind_value(paper, 'selected').classes('scale-150 ml-2')
                                with ui.column().classes('flex-1 min-w-0'):
                                    ui.label(paper['id']).classes('text-sm font-mono text-indigo-600 font-bold mb-1')
                                    ui.label(paper['title']).classes('text-xl font-semibold leading-snug text-slate-800 break-words')
                                
                                with ui.row().classes('items-center gap-2'):
                                    ui.button(icon='download', on_click=lambda p=paper: downloader.download_papers([p])).props('flat round color=green size=lg')

    # Initialize selects
    group_select.value = 'grp_cs'
    update_archives('grp_cs')

ui.run(title="ArXiv Downloader", reload=False, port=8080)
