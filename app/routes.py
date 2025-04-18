from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from utils.processing import process_shapefile_and_find_stations
from utils.map import generate_map

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    return '''
    <h1>Upload Project Area Shapefile (ZIP)</h1>
    <p>Please upload a ZIP file that contains the full set of shapefile components (.shp, .shx, .dbf, and .prj).</p>
    <p><strong>Important Notes:</strong></p>
    <ul>
        <li>The shapefile must represent a <strong>single polygon</strong>, not a multipolygon or multiple disconnected features.</li>
        <li>The polygon must be <strong>correctly projected</strong> with a defined coordinate system (ideally <code>.prj</code> file included).</li>
        <li>A <strong>single polygon</strong> is a closed, 2D shape with one outer boundary and optionally holes. A <em>multipolygon</em> contains two or more disjoint shapes and is <strong>not supported</strong>.</li>
    </ul>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="file" accept=".zip"/>
      <button type="submit">Upload</button>
    </form>
    '''
@router.get("/favicon.ico")
async def favicon():
    return HTMLResponse(status_code=204)  # No content, avoids 404 log

@router.post("/upload", response_class=HTMLResponse)
async def upload_shapefile(file: UploadFile = File(...)):
    import os
    os.makedirs("data", exist_ok=True)  # <- ensure data/ exists
    zip_path = f"data/{file.filename}"
    contents = await file.read()
    with open(zip_path, "wb") as f:
        f.write(contents)

    filtered_stations, stations_txt_path, map_html = process_shapefile_and_find_stations(zip_path)
    return f'''
    <h2>Results</h2>
    <p><strong>Note:</strong> Green dots are streamflow gaging stations <strong>within the project area</strong>. 
    Red dots are stations <strong>outside the project area</strong>, but within <strong>20 miles</strong> of the project boundary.</p>

    <p><em>The station metadata has been saved to:</em> <code>{stations_txt_path}</code></p>

    <div style="height: 600px; overflow: hidden; border: 1px solid #ccc; margin-top: 10px;">
        {map_html}
    </div>
    '''

