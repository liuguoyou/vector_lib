#!/usr/bin/env python

"""Ninja build configurator for vector library"""

import sys
import os

sys.path.insert(0, os.path.join('build', 'ninja'))

import generator

dependlibs = ['foundation']

generator = generator.Generator(project = 'vector', dependlibs = dependlibs, variables = [('bundleidentifier', 'com.rampantpixels.vector.$(binname)')])
target = generator.target
writer = generator.writer
toolchain = generator.toolchain

vector_lib = generator.lib(module = 'vector', sources = [
  'vector.c', 'version.c'])

if not target.is_ios() and not target.is_android() and not target.is_tizen():
  configs = [config for config in toolchain.configs if config not in ['profile', 'deploy']]
  if not configs == []:
    generator.bin('maskgen', ['main.c'], 'maskgen', basepath = 'tools', implicit_deps = [vector_lib], libs = ['vector', 'foundation'], configs = configs)

#No test cases if we're a submodule
if generator.is_subninja():
  sys.exit()

includepaths = generator.test_includepaths()

test_cases = [
  'matrix', 'quaternion', 'vector'
]
if toolchain.is_monolithic() or target.is_ios() or target.is_android() or target.is_tizen() or target.is_pnacl():
  #Build one fat binary with all test cases
  test_resources = []
  test_extrasources = []
  test_cases += ['all']
  if target.is_ios():
    test_resources = [os.path.join('all', 'ios', item) for item in ['test-all.plist', 'Images.xcassets', 'test-all.xib']]
    test_extrasources = [os.path.join('all', 'ios', 'viewcontroller.m')]
  elif target.is_android():
    test_resources = [os.path.join('all', 'android', item) for item in [
      'AndroidManifest.xml', os.path.join('layout', 'main.xml'), os.path.join('values', 'strings.xml'),
      os.path.join('drawable-ldpi', 'icon.png'), os.path.join('drawable-mdpi', 'icon.png'), os.path.join('drawable-hdpi', 'icon.png'),
      os.path.join('drawable-xhdpi', 'icon.png'), os.path.join('drawable-xxhdpi', 'icon.png'), os.path.join('drawable-xxxhdpi', 'icon.png')
    ]]
    test_extrasources = [os.path.join('all', 'android', 'java', 'com', 'rampantpixels', 'vector', 'test', item) for item in [
      'TestActivity.java'
    ]]
  elif target.is_tizen():
    test_resources = [os.path.join('all', 'tizen', item) for item in [
      'tizen-manifest.xml', os.path.join('res', 'tizenapp.png')
    ]]
  if target.is_ios() or target.is_android() or target.is_tizen():
    generator.app(module = '', sources = [os.path.join(module, 'main.c') for module in test_cases] + test_extrasources, binname = 'test-all', basepath = 'test', implicit_deps = [vector_lib], libs = ['test', 'vector'] + dependlibs, resources = test_resources, includepaths = includepaths)
  else:
    generator.bin(module = '', sources = [os.path.join(module, 'main.c') for module in test_cases] + test_extrasources, binname = 'test-all', basepath = 'test', implicit_deps = [vector_lib], libs = ['test', 'vector'] + dependlibs, resources = test_resources, includepaths = includepaths)
else:
  #Build one binary per test case
  generator.bin(module = 'all', sources = ['main.c'], binname = 'test-all', basepath = 'test', implicit_deps = [vector_lib], libs = ['vector'] + dependlibs, includepaths = includepaths)
  for test in test_cases:
    generator.bin(module = test, sources = ['main.c'], binname = 'test-' + test, basepath = 'test', implicit_deps = [vector_lib], libs = ['test', 'vector'] + dependlibs, includepaths = includepaths)
