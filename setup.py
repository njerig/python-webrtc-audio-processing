#!/usr/bin/env python
# encoding: utf-8
"""
Python bindings of webrtc audio processing
"""

from glob import glob
import platform
import sys
from setuptools import setup, Extension
import os

with open('README.md') as f:
    long_description = f.read()

include_dirs = ['src', 'webrtc-audio-processing']
libraries = ['pthread', 'stdc++']
define_macros = [
    ('WEBRTC_POSIX', None),
    ('WEBRTC_NS_FLOAT', None),
    ('WEBRTC_AUDIO_PROCESSING_ONLY_BUILD', None)
]

if platform.system() != 'Darwin':
    define_macros.append(('WEBRTC_LINUX', None))

extra_compile_args = ['-std=c++11'] if platform.system() != 'Darwin' else []

ap_sources = []
ap_dir_prefix = 'webrtc-audio-processing/webrtc/'
for i in range(8):
    ap_sources += glob(ap_dir_prefix + '*.c*')
    ap_dir_prefix += '*/'

# Filter out Windows-specific files
ap_sources = [src for src in ap_sources if not ('win.cc' in src.lower() or 'win.h' in src.lower())]

rw_lock_generic_path = os.path.join('webrtc-audio-processing', 'webrtc', 'system_wrappers', 'source', 'rw_lock_generic.cc')
condition_variable_path = os.path.join('webrtc-audio-processing', 'webrtc', 'system_wrappers', 'source', 'condition_variable.cc')

if rw_lock_generic_path in ap_sources:
    ap_sources.remove(rw_lock_generic_path)

if condition_variable_path in ap_sources:
    ap_sources.remove(condition_variable_path)

def get_yocto_var(var_name):
    val = os.environ.get(var_name, None)
    if val is None:
        raise Exception(f'Bitbake build detected, i.e. BB_CURRENT_TASK is set, but {var_name} is not set. Please do export {var_name} in your bitbake recipe.')
    return val

def process_arch(arch, set_compile_flags=False):
    global ap_sources, define_macros, extra_compile_args
    if arch.find('arm') >= 0:
        ap_sources = [src for src in ap_sources if src.find('mips.') < 0 and src.find('sse') < 0]
        define_macros.append(('WEBRTC_HAS_NEON', None))
        if platform.system() == 'Darwin' and arch.find('arm64') >= 0:
            if ('WEBRTC_LINUX', None) in define_macros:
                define_macros.remove(('WEBRTC_LINUX', None))
            define_macros.extend([
                ('WEBRTC_MAC', None),
                ('WEBRTC_ARCH_ARM64', None),
                ('WEBRTC_CLOCK_TYPE_REALTIME', None)
            ])
            extra_compile_args.clear()
        else:
            if set_compile_flags:
                extra_compile_args.append('-mfloat-abi=hard')
                extra_compile_args.append('-mfpu=neon')
    elif arch.find('aarch64') >= 0:
        ap_sources = [src for src in ap_sources if src.find('mips.') < 0 and src.find('sse') < 0]
        define_macros.append(('WEBRTC_HAS_NEON', None))
        define_macros.append(('WEBRTC_ARCH_ARM64', None))
    elif arch.find('x86') >= 0:
        ap_sources = [src for src in ap_sources if src.find('mips.') < 0 and src.find('neon.') < 0]
    elif arch.find('mips') >= 0:
        ap_sources = [src for src in ap_sources if src.find('mips.') < 0 and src.find('neon.') < 0]
    else:
        raise Exception('Unsupported arch: %s' % arch)

if 'BITBAKE_BUILD' in os.environ:
    print('Building with bitbake build system')
    cc_args = get_yocto_var('TARGET_CC_ARCH')
    extra_compile_args += cc_args.split()

    target_sys = get_yocto_var('TARGET_SYS')
    process_arch(target_sys)
else:
    process_arch(platform.machine(), set_compile_flags=platform.system() != 'Darwin')

sources = (
    ap_sources +
    ['src/audio_processing_module.cpp', 'src/webrtc_audio_processing.i']
)

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
            libraries=libraries,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args
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