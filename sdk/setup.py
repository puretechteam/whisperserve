from setuptools import setup

setup(
    name="whisperserve-sdk",
    version="0.1.0",
    description="Python SDK for the WhisperServe Audio Transcription API",
    packages=["sdk"],
    package_dir={"sdk": "."},
    install_requires=[
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
)