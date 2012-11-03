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
#			 xmv "^\[hdreactor.org\]_*" ""
#		
#		* Moviendo canciones en formato mp3 de la agrupacion musical HIM a una carpeta llamada HIM
#			 xmv "^HIM-(.+)$" "HIM/\1" "*.mp3"
#
#		* Moviendo archivos que coincidan con una expresion regular a un directorio
#			xmv "^\[hdreactor.org\].*$" "/home/emilio/\g<0>"
#
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


class Move:
	"""Mover archivo a destino"""
	
	def __init__(self, overwrite, suffix, verbose, listener):
		""" Constructor """
		
		self.overwrite = overwrite
		self.suffix = suffix
		self.verbose = verbose
		self.listener = listener
		
	def apply(self, source, destination):
		"""Mueve los archivos"""

		filename = os.path.basename(source)

		# Si se forza sobrescribir 
		if self.overwrite:
			# Mover archivo
			shutil.move(source, destination)
			
			if self.verbose:
				self.listener.notify_moved(filename, destination)
			
		elif self.suffix: # Si se utiliza sufijo
		
			# Si ya existe, intenta generar siguiendo una secuencia
			i = 0
			base_destination = destination
			while os.path.exists(destination):
				i+=1
				destination = re.sub("\.([^\.])*$", str(i) + "(\g<0>)", base_destination)

			# Mover archivo
			shutil.move(source, destination)
			
			if self.verbose:
				self.listener.notify_moved(filename, destination)
			
		elif os.path.exists(destination): # Con confirmacion
			
			confirm = self.listener.notify_confirm_overwrite(filename, destination)
			
			if confirm == "y":
				# Mover archivo
				shutil.move(source, destination)
				
				if self.verbose:
					self.listener.notify_moved(filename, destination)

		else:
			# Mover archivo
			shutil.move(source, destination)
			
			if self.verbose:
				self.listener.notify_moved(filename, destination)


class MoveSubstitution:
	"""Mover archivos que coincidan con el patron utilizando sustitución con expresión regular re.sub"""
	
	def __init__(self, pattern, replacement, ignore_case, overwrite, suffix, verbose, listener):
		""" Constructor """
		
		self.pattern = pattern
		self.replacement = replacement
		self.ignore_case = ignore_case
		self.move = Move(overwrite, suffix, verbose, listener)
		
	def apply(self, source):
		"""Mueve los archivos"""

		for file_path in glob.iglob(source):
			filename = os.path.basename(file_path)
			
			if self.ignore_case:
				destination = re.sub(self.pattern, self.replacement, filename, flags=re.IGNORECASE)
			else:
				destination = re.sub(self.pattern, self.replacement, filename)
			
			# Si se ha realizado sustitucion
			if filename != destination:
				self.move.apply(file_path, destination)		
					
class Listener:
	"""Oyente"""
	
	def __init__(self, view):
		""" Constructor """
		
		self.view = view

	def notify_confirm_overwrite(self, filename, destination):
		""" Notificar confirmacion de sobrescritura """
		
		return self.view.confirm_overwrite(filename, destination)
		
		
	def notify_moved(self, filename, destination):
		""" Notificar archivo movido """

		return self.view.display_moved(filename, destination)


class View:
	""" Vista de la aplicacion """

	def __init__(self):
		"""Constructor"""
		
		self.parser = argparse.ArgumentParser(description='Mueve los archivos que encajen con el patrón a la ruta apuntada por la cadena de remplazo')
		self.parser.add_argument("pattern", help="Patrón con el que debe coincidir, es una expresión regular de python")
		self.parser.add_argument("replacement", help="Cadena de remplazo valida de expresiones regulares de python utilizada como destino")
		self.parser.add_argument("source", help="Path fuente (corresponde una expresión regular path de UNIX)", nargs="?", default="*")
		
		group = self.parser.add_mutually_exclusive_group()
		group.add_argument("-o", "--overwrite", action="store_true", help="Sobrescribir archivos")
		group.add_argument("-s", "--suffix", action="store_true", help="Usar sufijo numérico cuando exista el archivo")
		
		self.parser.add_argument("-i", "--ignore-case",action="store_true", help="Ignorar mayúsculas")
		self.parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar lista de archivos movidos")
		
		
	def get_args(self):
		"""Obtiene los argumentos"""

		return self.parser.parse_args()
		
		
	def get_listener(self):
		""" Obtener oyente """
		
		return Listener(self)
	
	
	def confirm_overwrite(self, filename, destination):
		""" Confirmar sobrescritura """
		
		while True:
			value = raw_input("Overwrite %s (y/n): " % destination)
			if value in ['y', 'n']:
				return value
		
	
	def display_moved(self, filename, destination):
		""" Mostrar archivo movido """
		
		print filename, "moved to", destination
		

class Controller:
	"""Controlador"""

	def main(self):
		view = View()
		args = view.get_args()
		
		move = MoveSubstitution(args.pattern, args.replacement, args.ignore_case, args.overwrite, args.suffix, args.verbose, view.get_listener())
		move.apply(args.source)
		return 0 
		 
		 
if __name__ == '__main__':
	Controller().main()

