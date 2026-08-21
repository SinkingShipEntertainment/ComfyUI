name = 'ComfyUI'

version = '0.24.1.sse.1.1.0'

description = 'ComfyUI'

authors = ['ComfyUI']

with scope('config') as c:
    import os
    c.release_packages_path = os.environ['SSE_REZ_REPO_RELEASE_EXT']

requires = [
    'comfyui_frontend_package-1.44.19',
    'comfyui_workflow_templates-0.9.98',
    'comfyui_embedded_docs-0.5.2',
    'python-3',
    'torch',
    'torchsde',
    'torchvision',
    'torchaudio',
    'numpy-1.25+',
    'einops',
    'transformers-4.50.3+',
    'tokenizers-0.13.3+',
    'sentencepiece',
    'safetensors-0.4.2+',
    'aiohttp-2.11.8+',
    'yarl-1.18.0+',
    'PyYAML',
    'pillow',
    'scipy',
    'tqdm',
    'psutil',
    'alembic',
    'SQLAlchemy-2.0.0+',
    'filelock',
    'av-16.0.0+',
    'comfy_kitchen-0.2.10',
    'comfy_aimdo-0.4.8',
    'requests',
    'simpleeval-1.0.0+',
    'blake3',

    'kornia-0.7.1+',
    'spandrel',
    'pydantic-2', # equivalent to pydantic~=2.0, which means "any version in the 2.x series"
    'pydantic_settings-2',
    'PyOpenGL',

    # The python wrapper for glfw (v2.1.0) is getting overruled by another
    # rez package also called glfw (v3.4.0). To get around this, the required
    # glfw package was installed and manually changed to "python_glfw"
    'python_glfw',
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
    # executable = "python3 {root}/main.py --auto-launch --base-directory ~/comfyui"
    executable = "python3 {root}/comfy_tray.py"

    alias("comfyui", executable)


build_command = 'rez python {root}/rez_build.py'
uuid = 'repository.ComfyUI'
