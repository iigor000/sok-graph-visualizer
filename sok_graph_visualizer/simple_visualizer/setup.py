from setuptools import setup, find_packages

setup(
    name="graph-simple-visualizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "graph-api",
        "jinja2",
    ],
    entry_points={
        'graph.visualizer': [
            'simple_vis = simple_visualizer.src.simple_visualizer:SimpleVisualizer',
        ],
    }
)