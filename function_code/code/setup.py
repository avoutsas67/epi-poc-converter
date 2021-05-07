
import setuptools
from datetime import datetime
from pathlib import Path
import os


current_file = Path().absolute()
print(f'Current file path: {current_file}')
# current_file_folder = Path(os.getcwd())
current_file_folder = Path().parent.absolute()
print(f"Current folder: {current_file_folder}")


path_readme = os.path.join(current_file_folder,"README.md")
with open(path_readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

modules_root = os.path.join(current_file)

package_name = current_file_folder.stem

modules_to_use = ['documentAnnotation',
    'extractContentBetweenHeadings',
    'fhirService',
    'fhirXmlGenerator',
    'htmlDocTypePartitioner',
    'languageInfo',
    'match',
    'parse',
    'QrdExtractor',
    'utils',
    'scripts'
    ]

path_requirements = os.path.join(current_file_folder,'requirements.txt')
package_dir = {}

with open(path_requirements, "r") as fh:
    requirements = [l.strip() for l in fh.readlines()]

packages = []

for module in modules_to_use:
    module_path = os.path.join(modules_root,module)
    packages = packages + setuptools.find_namespace_packages(where=modules_root, include=[f'{module}*'])
    package_dir[module] = module_path

today = datetime.today()
version = f'{today:%Y}{today:%m}{today:%d}_{today:%H}{today:%M}{today:%S}'

setuptools.setup(
    name=package_name,
    version=version,
    author="Vipul Sharma",
    author_email="vipsharm@microsoft.com",
    description="Document Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    package_dir=package_dir,
    install_requires=requirements,
    python_requires='~=3.7.3'
)
