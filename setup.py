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
import sys
import shutil

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

if platform.system() == 'Linux':
    # on Linux, libraries may be in architecture-specific subdirectories
    lib_base = install_dir / 'lib'
    
    # try to find architecture-specific directory
    arch_dirs = []
    if lib_base.exists():
        for item in lib_base.iterdir():
            if item.is_dir() and '-' in item.name and 'linux' in item.name.lower():
                arch_dirs.append(item)
    
    # check if library exists in architecture-specific directory
    lib_path = None
    if arch_dirs:
        for arch_dir in arch_dirs:
            candidate = arch_dir / lib_name
            if candidate.exists():
                lib_path = candidate
                break
    
    # fallback to lib/ if not found in architecture-specific directory
    if lib_path is None:
        lib_path = lib_base / lib_name
else:
    lib_path = install_dir / 'lib' / lib_name

# check if webrtc-audio-processing submodule is initialized
if not webrtc_dir.exists() or not any(webrtc_dir.iterdir()):
    print("WebRTC audio processing submodule not initialized. Initializing...")
    try:
        subprocess.check_call(['git', 'submodule', 'update', '--init', '--recursive'], cwd=setup_dir)
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialize submodule: {e}")
        print("Please run 'git submodule update --init --recursive' manually")
        sys.exit(1)

# clean up any existing install directory that might be a file
if install_dir.exists() and not install_dir.is_dir():
    print(f"Removing existing file at {install_dir}")
    install_dir.unlink()

# check if we need to build or rebuild
need_build = False
if not lib_path.exists():
    need_build = True
    print("Library not found, will build WebRTC audio processing library...")
else:
    # check if abseil headers are available
    install_include = install_dir / 'include'
    if not install_include.exists():
        need_build = True
        print("Include directory missing, will rebuild...")
    else:
        # check for abseil headers specifically
        abseil_header = install_include / 'absl' / 'base' / 'nullability.h'
        if not abseil_header.exists():
            # try to find abseil in subprojects
            found_abseil = False
            subprojects_dir = webrtc_dir / 'subprojects'
            if subprojects_dir.exists():
                for path in subprojects_dir.iterdir():
                    if path.is_dir() and 'abseil' in path.name:
                        test_header = path / 'absl' / 'base' / 'nullability.h'
                        if test_header.exists():
                            found_abseil = True
                            break
            
            if not found_abseil:
                need_build = True
                print("Abseil headers not found, will rebuild...")
            else:
                print(f"Using existing WebRTC library at {lib_path}")
        else:
            print(f"Using existing WebRTC library at {lib_path}")

# build WebRTC if needed
if need_build:
    print("Building WebRTC audio processing library...")
    
    # check if meson.build exists
    meson_build_file = webrtc_dir / 'meson.build'
    if not meson_build_file.exists():
        print(f"Error: {meson_build_file} not found. The webrtc-audio-processing submodule may not be properly initialized.")
        print("Please ensure the submodule is properly initialized with:")
        print("  git submodule update --init --recursive")
        sys.exit(1)
    
    # check if the abseil wrap file exists in the correct location
    subprojects_dir = webrtc_dir / 'subprojects'
    abseil_wrap = subprojects_dir / 'abseil-cpp.wrap'
    
    if not subprojects_dir.exists():
        print(f"Creating subprojects directory at {subprojects_dir}")
        subprojects_dir.mkdir(parents=True, exist_ok=True)
    
    if not abseil_wrap.exists():
        print(f"Warning: abseil-cpp.wrap not found at {abseil_wrap}")
        print("Meson may fail to download the abseil dependency")
        print("Please ensure the wrap file is in place")
    
    # clean up build directory if it exists
    if build_dir.exists():
        print("Cleaning up existing build directory...")
        shutil.rmtree(build_dir)
    
    original_cwd = os.getcwd()
    
    try:
        # change to webrtc directory for all meson operations
        os.chdir(str(webrtc_dir))
        
        # first, download subprojects before setup
        print("Downloading subprojects...")
        try:
            subprocess.check_call(['meson', 'subprojects', 'download'])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to download subprojects: {e}")
            print("Meson will try to download them during setup")
        
        # configure with meson
        print("Configuring build with meson...")
        subprocess.check_call([
            'meson',
            'setup',
            'build',
            f'--prefix={install_dir}',
            '--wrap-mode=forcefallback',
            '--force-fallback-for=abseil-cpp',
            '--buildtype=release',
            '-Ddefault_library=shared',
        ])
        
        # build
        print("Building with ninja...")
        subprocess.check_call([
            'ninja',
            '-C',
            'build'
        ])
        
        # install
        print("Installing...")
        subprocess.check_call([
            'ninja',
            '-C',
            'build',
            'install'
        ])
        
        # Fix library install_name on macOS for proper rpath resolution
        if platform.system() == 'Darwin':
            # Fix both the symlink target (2.1) and the symlink itself (2)
            lib_file_21 = install_dir / 'lib' / 'libwebrtc-audio-processing-2.1.dylib'
            lib_file = install_dir / 'lib' / lib_name
            
            for lib_to_fix, lib_name_for_fix in [(lib_file_21, 'libwebrtc-audio-processing-2.1.dylib'), 
                                                   (lib_file, lib_name)]:
                if lib_to_fix.exists() and not lib_to_fix.is_symlink():
                    print(f"Fixing library install name for {lib_name_for_fix}...")
                    try:
                        # Set install_name to use @rpath so our rpath settings work
                        subprocess.check_call([
                            'install_name_tool',
                            '-id',
                            f'@rpath/{lib_name_for_fix}',
                            str(lib_to_fix)
                        ])
                        print(f"Library install name fixed to @rpath/{lib_name_for_fix}")
                    except subprocess.CalledProcessError as e:
                        print(f"Warning: Failed to fix library install name: {e}")
                        print("Extension may still work if rpath is set correctly")
                    except FileNotFoundError:
                        print("Warning: install_name_tool not found. This may cause runtime issues.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to build WebRTC library: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure meson and ninja are installed:")
        print("   pip install meson ninja")
        print("2. Check that the abseil-cpp.wrap file is in:")
        print(f"   {abseil_wrap}")
        print("3. Try running meson directly in the webrtc directory:")
        print(f"   cd {webrtc_dir}")
        print("   meson subprojects download")
        print("   meson setup build")
        sys.exit(1)
    finally:
        os.chdir(original_cwd)
    
    if need_build:
        print(f"WebRTC library built at {lib_path}")
    else:
        # Fix install_name for existing library on macOS
        if platform.system() == 'Darwin':
            # Fix both the actual library (2.1) and symlink (2)
            lib_file_21 = install_dir / 'lib' / 'libwebrtc-audio-processing-2.1.dylib'
            lib_file = install_dir / 'lib' / lib_name
            
            for lib_to_fix, lib_name_for_fix in [(lib_file_21, 'libwebrtc-audio-processing-2.1.dylib'), 
                                                   (lib_file, lib_name)]:
                if lib_to_fix.exists() and not lib_to_fix.is_symlink():
                    print(f"Checking library install name for {lib_name_for_fix}...")
                    try:
                        # Check current install name
                        result = subprocess.run(
                            ['otool', '-D', str(lib_to_fix)],
                            capture_output=True,
                            text=True
                        )
                        current_name = result.stdout.strip().split('\n')[-1] if result.stdout else ''
                        
                        # Fix if not using @rpath
                        if '@rpath' not in current_name:
                            print(f"Fixing library install name from {current_name}...")
                            subprocess.check_call([
                                'install_name_tool',
                                '-id',
                                f'@rpath/{lib_name_for_fix}',
                                str(lib_to_fix)
                            ])
                            print(f"Library install name fixed to @rpath/{lib_name_for_fix}")
                        else:
                            print(f"Library install name already correct: {current_name}")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Non-critical, continue anyway
                        pass

# read in README as description
with open('README.md') as f:
    long_description = f.read()

os_name = platform.system()
machine = platform.machine()

sources = [
    'src/audio_processing_module.cpp', 
    'src/webrtc_audio_processing.i',
    'webrtc-audio-processing/webrtc/common_audio/vad/vad.cc'
]

# find the actual abseil include directory
abseil_include = None
subprojects_dir = webrtc_dir / 'subprojects'
if subprojects_dir.exists():
    # look for abseil directories
    for path in subprojects_dir.iterdir():
        if path.is_dir() and 'abseil' in path.name:
            abseil_include = str(path)
            print(f"Found abseil at: {abseil_include}")
            break
    
    # if not found in direct subdirectories, check packagecache
    if not abseil_include:
        packagecache = subprojects_dir / 'packagecache'
        if packagecache.exists():
            for path in packagecache.iterdir():
                if path.is_dir() and 'abseil' in path.name:
                    abseil_include = str(path)
                    print(f"Found abseil in packagecache at: {abseil_include}")
                    break

# also check the install directory for abseil headers
install_include = install_dir / 'include'
if install_include.exists():
    print(f"Found install include directory at: {install_include}")

include_dirs = [
    'src', 
    'webrtc-audio-processing',
    'webrtc-audio-processing/webrtc',
]

# add abseil include if found
if abseil_include:
    include_dirs.append(abseil_include)
else:
    # fallback to expected location
    include_dirs.append('webrtc-audio-processing/subprojects/abseil-cpp-20240722.0')
    print("Warning: Could not find abseil directory, using default path")

# add install include directory if it exists
if install_include and install_include.exists():
    include_dirs.append(str(install_include))
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

# on macOS, link by name and use rpath, don't link directly to file path
if os_name == 'Darwin':
    lib_dir = install_dir / 'lib'

    extra_link_args = [f'-L{lib_dir}', '-lwebrtc-audio-processing-2.1']
    # set rpath so extension can find library
    extra_link_args.append(f'-Wl,-rpath,{lib_dir}')
    extra_link_args.append('-Wl,-rpath,@loader_path/../webrtc-audio-processing/install/lib')
else:
    # on Linux, link by name and use rpath
    if lib_path and lib_path.exists():
        lib_dir = lib_path.parent
    else:
        lib_dir = install_dir / 'lib'
    extra_link_args = [f'-L{lib_dir}', '-lwebrtc-audio-processing-2']
    # set rpath so extension can find library at runtime
    extra_link_args.append(f'-Wl,-rpath,{lib_dir}')

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