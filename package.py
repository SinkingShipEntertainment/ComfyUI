name = 'ComfyUI'

version = '0.13.0.sse.1.0.0'

description = 'ComfyUI'

authors = ['ComfyUI']

with scope('config') as c:
    import os
    c.release_packages_path = os.environ['SSE_REZ_REPO_RELEASE_EXT']

# requires = [
#     'python-3',
#     'aiohttp',
#     'einops',
#     'fairscale',
#     'kornia-0.6.9',
#     'pillow',
#     'PyYAML',
#     'psutil',
#     'safetensors',
#     'scipy',
#     'torch',
#     'torchsde',
#     'torchaudio',
#     'torchdata',
#     'torchmetrics',
#     'torchvision',
#     'tqdm',
#     'transformers-4.19.1',
#     'sse_nvidia_cuda-12'
# ]

requires = [
    'comfyui_frontend_package-1.38.13',
    'comfyui_workflow_templates-0.8.38',
    'comfyui_embedded_docs-0.4.1',
    'python-3',
    'torch',
    'torchsde',
    'torchvision',
    'torchaudio',
    'numpy',
    'einops',
    'transformers',
    'tokenizers',
    'sentencepiece',
    'safetensors',
    'aiohttp',
    'yarl',
    'PyYAML',
    'pillow',
    'scipy',
    'tqdm',
    'psutil',
    'alembic',
    'SQLAlchemy',
    'av',
    'comfy_kitchen',
    'comfy_aimdo',
    'requests',

    'kornia',
    'spandrel',
    'pydantic',
    'pydantic_settings',
]

private_build_requires = []

variants = []

def commands():
    env.REZ_COMFYUI_ROOT = '{root}'
    env.PYTHONPATH.append('{root}')

    # NOTE: REZ package versions can have ".sse." to separate the external
    # version from the internal modification version.
    split_versions = str(version).split(".sse.")
    external_version = split_versions[0]
    internal_version = None
    if len(split_versions) == 2:
        internal_version = split_versions[1]

    env.COMFYUI_VER = external_version
    env.COMFYUI_SSE_VERSION = external_version
    if internal_version:
        env.COMFYUI_SSE_VERSION = internal_version

    # Alias
    executable = "python3 {root}/main.py --auto-launch --base-directory ~/comfyui"

    alias("comfyui", executable)


build_command = 'rez python {root}/rez_build.py'
uuid = 'repository.ComfyUI'
