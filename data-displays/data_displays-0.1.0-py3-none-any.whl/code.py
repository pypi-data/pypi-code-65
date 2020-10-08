from time import sleep
from math import floor
from threading import Thread
from threading import enumerate as allthreads

class data:
	threads = []
	lines = []

	class bar:
		def create(label="", duration=0, length=0, lineno=1, size=0, unit=""):
			data.threads.append(
				Thread(
					target=data.bar.thread,
					args=(
						(
							(
								" " + str(
									label
								).strip(
								) + ":" if str(
									label
								).strip(
								) else ""
							) if len(
								(
									" " + str(
										label
									).strip(
									) + ":"
								) if str(
									label
								).strip(
								) else ""
							) < int(
								length
							) else
						 	(
								" " + str(
									label
								).strip(
								)
							)[
								0:floor(
									(
										int(
											length
										)
									) - 4
								)
							].rstrip(
							) + "\u2026:".strip(
							)
						),
						int(
							duration
						),
						int(
							length
						),
						int(
							lineno
						),
						int(
							size
						),
						str(
							unit
						),
					)
				)
			)
			data.lines.append(lineno)
			data.threads[-1].start(
			)

		def thread(label, duration, length, lineno, size, unit):
			print(
				end="\u001b[?25l"
			)
			for percent in range(0, 101):
				print(
					end="\u001b[1000A\u001b[" + str(lineno) +
					("B\u001b[2K\r" if label else "B\r") + 
					label.lower(
					).capitalize(
					) + "\u001b[1B\u001b[2K\r" + 
					(
						"\u001b[7m \u001b[0m" * floor(
							(
								length - (
									10 + len(
										str(
											size
										) + str(
											unit
										)
									)
								)
							) * percent / 100
						)
					) + "\r\u001b[" + str(
						floor(
							length - (
								10 + len(
									str(
										size
									) + str(
										unit
									)
								)
							)
						)
					) + "C\u001b[0m|" + (
						str(
							round(
								percent
							)
						) + "% -- " + str(
						floor(
								(
									size / 100
								) * percent
							)
						) + " " + unit.lower(
						).capitalize(
						) + "\r|" if size else "\u001b[0m\r|"
					)
				)
				sleep(
					duration / 100
				)
			return None

	def wait():
		data.threads
		for thread in data.threads:
			thread.join(
			)

		print(
			end="\u001b[?25h\u001b[1000A\u001b[" + str(
				max(
					data.lines
				) + 2
			) + "B"
		)

		data.threads = allthreads(
		)
