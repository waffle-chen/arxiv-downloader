import os
import re
import json
import asyncio
from nicegui import ui, app
from playwright.async_api import async_playwright
import webbrowser

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

    async def fetch_papers(self, subject, date, include_abs):
        self.is_loading = True
        ui.notify(f"Fetching papers for {subject} on {date}...")
        self.results = []
        
        async with async_playwright() as p:
            # Use chrome channel as requested for company environments
            browser = await p.chromium.launch(channel="chrome", headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            url = f"https://arxiv.org/catchup?subject={subject}&date={date}"
            if include_abs:
                url += "&include_abs=True"
            
            print(f"Navigating to {url}")
            await page.goto(url)
            
            # Simple parsing of the results page
            # ArXiv results are usually in <dl> with <dt> containing the link and <dd> the metadata
            papers = await page.query_selector_all("dl > dt")
            for dt in papers:
                # Find the PDF link
                pdf_link_el = await dt.query_selector('a[title="Download PDF"]')
                if not pdf_link_el:
                    continue
                
                pdf_url = await pdf_link_el.get_attribute("href")
                if not pdf_url.startswith("http"):
                    pdf_url = "https://arxiv.org" + pdf_url
                
                # Get ID
                paper_id_el = await dt.query_selector('a[id^="pdf-"]')
                paper_id = await paper_id_el.inner_text() if paper_id_el else "Unknown"
                
                # Get Title (usually in the following <dd>)
                dd = await page.evaluate_handle("el => el.nextElementSibling", dt)
                title_el = await dd.query_selector(".list-title")
                title = await title_el.inner_text() if title_el else "No Title"
                title = title.replace("Title: ", "").strip()
                
                self.results.append({
                    "id": paper_id,
                    "title": title,
                    "pdf_url": pdf_url,
                    "selected": False
                })
            
            await browser.close()
        
        self.is_loading = False
        if not self.results:
            ui.notify("No papers found for the selected criteria.", type="warning")
        else:
            ui.notify(f"Found {len(self.results)} papers.")

    async def download_paper(self, paper):
        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="chrome", headless=True)
            page = await browser.new_page()
            
            filename = f"{paper['id'].replace(':', '_')}.pdf"
            filepath = os.path.join(self.download_dir, filename)
            
            ui.notify(f"Downloading {paper['id']}...")
            
            # Playwright handles downloads
            async with page.expect_download() as download_info:
                await page.goto(paper['pdf_url'])
            
            download = await download_info.value
            await download.save_as(filepath)
            await browser.close()
            ui.notify(f"Downloaded to {filepath}", type="positive")

downloader = ArXivDownloader()

@ui.page('/')
def main_page():
    ui.colors(primary='#1a237e', secondary='#303f9f', accent='#ff4081')
    
    with ui.header().classes('items-center justify-between'):
        ui.label('ArXiv Catchup Downloader').classes('text-2xl font-bold')
        ui.button(icon='settings', on_click=lambda: ui.notify('Settings not implemented')).flat()

    with ui.column().classes('w-full p-8 max-w-4xl mx-auto'):
        with ui.card().classes('w-full p-6 shadow-lg'):
            ui.label('Search Criteria').classes('text-xl font-semibold mb-4')
            
            with ui.row().classes('w-full gap-4'):
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

            with ui.row().classes('w-full gap-4 items-end mt-4'):
                date_input = ui.date(value='2026-05-14').classes('hidden')
                with ui.button(icon='event'):
                    ui.menu().props('no-parent-event')
                    ui.date().bind_value(date_input)
                
                ui.label().bind_text_from(date_input, 'value', backward=lambda v: f"Date: {v}")
                
                include_abs = ui.checkbox('Include Abstracts', value=True)
                
                ui.button('Fetch Papers', on_click=lambda: start_fetch()).classes('ml-auto px-8')

        # Results area
        results_container = ui.column().classes('w-full mt-8')

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
        
        await downloader.fetch_papers(subject, date_input.value, include_abs.value)
        refresh_results()

    def refresh_results():
        results_container.clear()
        if not downloader.results:
            return
        
        with results_container:
            ui.label(f"Results ({len(downloader.results)})").classes('text-xl font-semibold mb-4')
            for paper in downloader.results:
                with ui.card().classes('w-full mb-2 p-4 hover:bg-slate-50 transition-colors'):
                    with ui.row().classes('w-full items-center justify-between'):
                        with ui.column().classes('flex-1'):
                            ui.label(paper['id']).classes('text-sm font-mono text-blue-600')
                            ui.label(paper['title']).classes('text-lg font-medium')
                        
                        ui.button('Download', on_click=lambda p=paper: downloader.download_paper(p)).props('outline')

    # Initialize selects
    group_select.value = 'grp_cs'
    update_archives('grp_cs')

ui.run(title="ArXiv Downloader", reload=False, port=8080)
