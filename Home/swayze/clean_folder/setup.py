print("Running setup.py...")

from setuptools import setup

setup(name="clean_folder",
      version="0.0.1",
      description="files sort script",
      author="Patrick Swayze",
      packages=["clean_folder"],
      entry_points={
          "console_scripts":["clean-folder = clean_folder.clean:main"]
      }
)
