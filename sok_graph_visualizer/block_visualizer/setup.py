from setuptools import setup, find_packages

setup(
    name="graph-block-visualizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "graph-api",
        "jinja2",
    ],
    entry_points={
        'graph.visualizer': [
            'block_vis = block_visualizer.src.block_visualizer:BlockVisualizer',
        ],
    }
)