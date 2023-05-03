import os
import zipfile
import glob
import shutil

try:
    import gdown
except ImportError:
    print(
        "The gdown package is required. Use `pip install gdown` to install it."
    )


def download_lectures(
    url=None,
    output=None,
    quiet=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
):
    """
    Downloads the lecture folder from GitHub repository and
    returns the output file path.
    """

    if output is None:
        if isinstance(url, str) and url.startswith("http"):
            output = os.path.basename(url)

    out_dir = os.path.abspath(os.path.dirname(output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(url, str):
        if os.path.exists(os.path.abspath(output)) and (not overwrite):
            print(
                f"{output} already exists. Skip downloading. Set overwrite=True to overwrite."
            )
            return os.path.abspath(output)

    output = gdown.download(url, output)

    if unzip and output.endswith(".zip"):
        with zipfile.ZipFile(output, "r") as zip_ref:
            if not quiet:
                print("Extracting files...")
            if subfolder:
                basename = os.path.splitext(os.path.basename(output))[0]

                output = os.path.join(out_dir, basename)
                if not os.path.exists(output):
                    os.makedirs(output)
                zip_ref.extractall(output)
            else:
                zip_ref.extractall(os.path.dirname(output))

    return os.path.abspath(output)


# This will fetch the lectures from latest main branch
LECTURE_INTRO_URL = "https://github.com/QuantEcon/lecture-python-intro/archive/refs/heads/main.zip"
out_zip = 'qe-lecture-intro-main.zip'

out_zip = download_lectures(LECTURE_INTRO_URL, out_zip)

in_dir = 'lecture-python-intro-main/lectures'
out_dir = 'content'
notebook_dir = os.path.abspath(os.path.join(out_dir, 'lectures'))

shutil.copytree(in_dir, notebook_dir, dirs_exist_ok=True)
cwd = os.getcwd()
os.chdir(cwd)


lectures = glob.glob(out_dir + '/lectures/*.md')

# Replace `!pip` with `%pip`
for file in lectures:
    with open(file, 'r') as f:
        lines = f.readlines()

    out_lines = []
    for index, line in enumerate(lines):
        if "!pip" in line:
            line_ = line.replace("!pip", "%pip")
            out_lines.append(line_)
        elif "! pip" in line:
            line_ = line.replace("! pip", "%pip")
            out_lines.append(line_)
        elif "pip" in line:
            line_ = line.replace("pip", "%pip")
            out_lines.append(line_)
        else:
            out_lines.append(line)

    with open(file, 'w') as f:
        f.writelines(out_lines)

os.chdir(notebook_dir)
cmd = "jupytext --to ipynb *.md"
os.system(cmd)
os.chdir(cwd)

for file in lectures:
    os.remove(file)

shutil.rmtree('lecture-python-intro-main')
os.remove(out_zip)
