#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	   xmv.py
#	   
#	   Mover archivos utilizando expresiones regulares
#
#	   Mueve archivos utilizando sustitución con expresiones regulares re.sub
#
#	   Ejemplos: 
#		* Eliminando prefijo en archivos del directorio de trabajo actual
#			 xmv "^\[hd_reactor\]_*"
#		
#		* Moviendo canciones en formato mp3 de la agrupacion musical HIM a una carpeta llamada HIM
#			 xmv "^HIM-(.+)$" "HIM/\1" "*.mp3"
#
#	   Copyright 2012 emilio <emilio.rst@gmail.com>
#	   
#	   This program is free software; you can redistribute it and/or modify
#	   it under the terms of the GNU General Public License as published by
#	   the Free Software Foundation; either version 2 of the License, or
#	   (at your option) any later version.
#	   
#	   This program is distributed in the hope that it will be useful,
#	   but WITHOUT ANY WARRANTY; without even the implied warranty of
#	   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	   GNU General Public License for more details.
#	   
#	   You should have received a copy of the GNU General Public License
#	   along with this program; if not, write to the Free Software
#	   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	   MA 02110-1301, USA.
#	   
#	   

import os
import re
import glob
import shutil
import argparse

def move(source, pattern, destiny, overwrite=False, suffix=False, verbose=False):
	"""Mover archivos que coincidan con el patron utilizando sustitución con expresión regular re.sub"""
	
	for file_path in glob.iglob(source):
		filename = os.path.basename(file_path)
		destination = re.sub(pattern, destiny, filename)
		 
		# Si se ha realizado sustitucion
		if filename != destination:
			
			# Si se forza sobrescribir 
			if overwrite:
				# Mover archivo
				shutil.move(file_path, destination)
				
				if verbose:
					print filename, "moved to", destination
				
			elif suffix: # Si se utiliza sufijo
			
				# Si ya existe, intenta generar siguiendo una secuencia
				i = 0
				base_destination = destination
				while os.path.exists(destination):
					i+=1
					destination = re.sub("\.([^\.])*$", str(i) + "(\g<0>)", base_destination)

				# Mover archivo
				shutil.move(file_path, destination)
				
				if verbose:
					print filename, "moved to", destination
				
			elif os.path.exists(destination): # Con confirmacion
				
				confirm = raw_input("Overwrite %s (y/n): " % destination)
				
				if confirm == "y":
					# Mover archivo
					shutil.move(file_path, destination)
					
					if verbose:
						print filename, "moved to", destination
	
			else:
				# Mover archivo
				shutil.move(file_path, destination)
				
				if verbose:
					print filename, "moved to", destination
		

def main():
	# Definiendo argumentos
	parser = argparse.ArgumentParser(description='Mueve los archivos que encajen con el patrón a la ruta apuntada por la cadena de remplazo')
	parser.add_argument("pattern", help="Patrón con el que debe coincidir, es una expresión regular de python")
	parser.add_argument("destiny", help="Cadena de remplazo valida de expresiones regulares de python utilizada como destino", nargs="?", default="")
	parser.add_argument("source", help="Path fuente (corresponde una expresión regular path de UNIX)", nargs="?", default="*")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-o", "--overwrite", action="store_true", help="Sobrescribir archivos")
	group.add_argument("-s", "--suffix", action="store_true", help="Usar sufijo numérico cuando exista el archivo")
	
	parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar lista de archivos movidos")
	args = parser.parse_args()
	
	# Mover archivos
	move(args.source, args.pattern, args.destiny, args.overwrite, args.suffix, args.verbose)
	return 0 
		 
		 
if __name__ == '__main__':
	main()

