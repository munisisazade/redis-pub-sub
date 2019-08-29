import setuptools
import sys
import os
import shutil
import subprocess
import platform

with open("README.md", "r") as fh:
    long_description = fh.read()
#
# config_files = []
# for dirpath, subdirs, files in os.walk("pydjango/conf/"):
#     print(dirpath, subdirs, files)
#     for dir in subdirs:
#         config_files.append(os.path.join(dirpath, dir))
#     for file in files:
#         config_files.append(os.path.join(dirpath, file))

if "install" in sys.argv:
    if platform.system() == "Windows":
        pass
    else:
        proc = subprocess.Popen("echo ~",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        path = proc.stdout.read().decode("utf-8").replace("\n", "")
        config_name = "{}/.pydjango".format(path)
        if not os.path.isdir(config_name):
            os.makedirs(config_name)
        if os.path.isdir("{}/conf".format(config_name)):
            subprocess.call("rm -rf {}/conf".format(config_name),shell=True)
        shutil.copytree("pydjango/conf", "{}/conf".format(config_name))
        file = open("pydjango/config.py", "w")
        file.write("conf_path='{}/conf'\n".format(config_name))
        file.close()
        print("la"*50)
    # os.path.join(path)

setuptools.setup(
    name="pydjango",
    version=__import__("pydjango").VERSION,
    author="Munis Isazade",
    author_email="munisisazade@gmail.com",
    description="PyDjango, create django application with command line interface.",
    long_description=long_description,
    license='MIT',
    url="https://github.com/munisisazade/pydjango",
    scripts=['pydjango/script/create_django.py'],
    install_requires=["jinja2"],
    entry_points={'console_scripts': [
        'create_django = pydjango.core.management:execute_from_command_line',
    ]},
    platforms=['any'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
