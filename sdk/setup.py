from setuptools import setup

with open("VERSION") as f:
    version = f.read().strip()

setup(
    name="whisperserve-sdk",
    version=version,
    description="Python SDK for the WhisperServe Audio Transcription API",
    packages=["sdk"],
    package_dir={"sdk": "."},
    install_requires=[
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
)