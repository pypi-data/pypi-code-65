import datetime


class Jalali:
	def __init__(self, datetime_value: datetime.datetime):
		self.datetime_value = datetime_value

	def gregorian_to_jalali(self, return_str=False, splitter='/'):
		gy, gm, gd = self.datetime_value.year, self.datetime_value.month, self.datetime_value.day

		g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
		if gy > 1600:
			jy = 979
			gy -= 1600
		else:
			jy = 0
			gy -= 621
		if gm > 2:
			gy2 = gy + 1
		else:
			gy2 = gy
		days = (365 * gy) + (int((gy2 + 3) / 4)) - (int((gy2 + 99) / 100)) + (int((gy2 + 399) / 400)) - 80 + gd + g_d_m[
			gm - 1]
		jy += 33 * (int(days / 12053))
		days %= 12053
		jy += 4 * (int(days / 1461))
		days %= 1461
		if days > 365:
			jy += int((days - 1) / 365)
			days = (days - 1) % 365
		if days < 186:
			jm = 1 + int(days / 31)
			jd = 1 + (days % 31)
		else:
			jm = 7 + int((days - 186) / 30)
			jd = 1 + ((days - 186) % 30)
		if return_str:
			return f'{jy}{splitter}{jm:02d}{splitter}{jd:02d}'
		return jy, jm, jd

	def date_diff_to_str_persian(self):
		"""
		mohasebeye ekhtelafe zamanie hal ba datetime_value va khorooji ba matne farsi
		:return:
		"""
		delta = datetime.datetime.now() - self.datetime_value
		if delta.days <= 0:
			if delta.seconds // 3600 >= 1:
				return f'{delta.seconds // 3600} ساعت قبل'
			else:
				return 'لحظاتی قبل'
		elif delta.days // 365 >= 1:
			return f'{delta.days // 365} سال قبل'
		elif delta.days // 30 >= 1:
			return f'{delta.days // 30} ماه قبل'
		else:
			return f'{delta.days} روز قبل'

	@staticmethod
	def jalali_to_gregorian(jy=0, jm=0, jd=0, return_datetime=False, jalali_date: str = None):
		if jalali_date is not None:
			jy, jm, jd = map(int, jalali_date.split("/"))

		if jy > 979:
			gy = 1600
			jy -= 979
		else:
			gy = 621
		if jm < 7:
			days = (jm - 1) * 31
		else:
			days = ((jm - 7) * 30) + 186
		days += (365 * jy) + ((int(jy / 33)) * 8) + (int(((jy % 33) + 3) / 4)) + 78 + jd
		gy += 400 * (int(days / 146097))
		days %= 146097
		if days > 36524:
			gy += 100 * (int(--days / 36524))
			days %= 36524
			if days >= 365:
				days += 1
		gy += 4 * (int(days / 1461))
		days %= 1461
		if days > 365:
			gy += int((days - 1) / 365)
			days = (days - 1) % 365
		gd = days + 1
		if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
			kab = 29
		else:
			kab = 28
		sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		gm = 0
		while gm < 13:
			v = sal_a[gm]
			if gd <= v:
				break
			gd -= v
			gm += 1

		if return_datetime:
			return datetime.date(gy, gm, gd)
		return gy, gm, gd
