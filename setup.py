#!/usr/bin/env python
# encoding: utf-8
"""
Python bindings of webrtc audio processing
"""

import platform
from setuptools import setup, Extension
import os
from pathlib import Path
import subprocess

# get the absolute path to the setup.py directory
setup_dir = Path(os.path.dirname(os.path.abspath(__file__)))
webrtc_dir = setup_dir / 'webrtc-audio-processing'
build_dir = webrtc_dir / 'build'
install_dir = webrtc_dir / 'install'

# make install_dir absolute
install_dir = install_dir.absolute()

if platform.system() == 'Darwin':
    lib_name = 'libwebrtc-audio-processing-2.dylib'
else:
    lib_name = 'libwebrtc-audio-processing-2.so'

lib_path = install_dir / 'lib' / lib_name

# build WebRTC if needed
if not lib_path.exists():
    print("Building WebRTC audio processing library...")
    
    original_cwd = os.getcwd()
    os.chdir(str(webrtc_dir))
    
    try:
        # configure with meson
        subprocess.check_call([
            'meson',
            'setup',
            'build',
            f'-Dprefix={install_dir}',
        ])
        
        # build
        subprocess.check_call([
            'ninja',
            '-C',
            'build'
        ])
        
        # install
        subprocess.check_call([
            'ninja',
            '-C',
            'build',
            'install'
        ])
    finally:
        os.chdir(original_cwd)
    
    print(f"WebRTC library built at {lib_path}")
else:
    print(f"Using existing WebRTC library at {lib_path}")

with open('README.md') as f:
    long_description = f.read()

os_name = platform.system()
machine = platform.machine()

sources = ['src/audio_processing_module.cpp', 'src/webrtc_audio_processing.i']

include_dirs = [
    'src', 
    'webrtc-audio-processing',
    'webrtc-audio-processing/webrtc',
    'webrtc-audio-processing/subprojects/abseil-cpp-20240722.0'
]
libraries = ['pthread', 'stdc++']
define_macros = [
    ('WEBRTC_AUDIO_PROCESSING_ONLY', None),
    ('WEBRTC_NS_FLOAT', None)
]

if os_name == 'Linux' or os_name == 'Darwin':
    define_macros.append(('WEBRTC_POSIX', None))
if os_name == 'Linux' or os_name == 'Android':
    define_macros.append(('WEBRTC_CLOCK_TYPE_REALTIME', None))

if os_name == 'Linux':
    define_macros.append(('WEBRTC_LINUX', None))
elif os_name == 'Darwin':
    define_macros.append(('WEBRTC_MAC', None))
elif os_name == 'Windows':
    define_macros.append(('WEBRTC_WIN', None))

extra_compile_args = ['-std=c++17']
extra_link_args = [str(lib_path)]

if machine in ['arm64', 'aarch64']:
    define_macros.extend([
        ('WEBRTC_HAS_NEON', None),
        ('WEBRTC_ARCH_ARM64', None)
    ])
elif 'arm' in machine:
    define_macros.append(('WEBRTC_HAS_NEON', None))
    extra_compile_args.extend(['-mfloat-abi=hard', '-mfpu=neon'])

swig_opts = (
    ['-c++'] +
    ['-I' + h for h in include_dirs]
)

setup(
    name='webrtc_audio_processing',
    version='0.1.3',
    description='Python bindings of webrtc audio processing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yihui Xiong',
    author_email='yihui.xiong@hotmail.com',
    url='https://github.com/xiongyihui/python-webrtc-audio-processing',
    download_url='https://pypi.python.org/pypi/webrtc_audio_processing',
    packages=['webrtc_audio_processing'],
    ext_modules=[
        Extension(
            name='webrtc_audio_processing._webrtc_audio_processing',
            sources=sources,
            swig_opts=swig_opts,
            include_dirs=include_dirs,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            libraries=libraries,
        )
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: C++'
    ],
    license='BSD',
    keywords=['webrtc audioprocessing', 'voice activity detection', 'noise suppression', 'automatic gain control'],
    platforms=['Linux', 'MacOS'],
    package_dir={
        'webrtc_audio_processing': 'src'
    },
    package_data={
        'webrtc_audio_processing': ['webrtc_audio_processing.py']
    }
)