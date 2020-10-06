import pandas as pd
from datetime import datetime

from dateutil.relativedelta import relativedelta


class Datev(object):
    def __init__(self, berater_nr: str, mandanten_nr):
        self.berater_nr = berater_nr
        self.mandanten_nr = mandanten_nr

    def get_template(self, valid_from: pd.datetime, use_alternative_employee_number=False):
        """
        This function is the place where you specify a custom output template to use when necessary. This template is used by the export_to_template function
        ----------
        :return: returns custom template or an error if no template is specified
        """
        template = f"""[Allgemein]
                             Ziel=LODAS
                             Version_SST=1.0
                             Version_DB=10.62
                             BeraterNr=508701
                             MandantenNr=28334
                             Kommentarzeichen=*
                             Feldtrennzeichen=;
                             Zahlenkomma=,
                             Datumsformat=TT/MM/JJJJ
                             StammdatenGueltigAb={valid_from}
                             {'BetrieblichePNrVerwenden=Ja' if use_alternative_employee_number else 'BetrieblichePNrVerwenden=Nein'}

                             [Satzbeschreibung]
                             100;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;duevo_familienname#psd;duevo_vorname#psd;gebname#psd;adresse_strassenname#psd;adresse_strasse_nr#psd;adresse_plz#psd;adresse_ort#psd;adresse_anschriftenzusatz#psd;adresse_plz_ausland#psd;
                             101;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;geburtsdatum_ttmmjj#psd;gebort#psd;geburtsland#psd;geschlecht#psd;sozialversicherung_nr#psd;staatsangehoerigkeit#psd;
                             102;u_lod_psd_ma_bank;pnr_betriebliche#psd;ma_iban#psd;ma_bic#psd;ma_bank_zahlungsart#psd;
                             103;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;schwerbeschaedigt#psd;mitarbeitertyp#psd;
                             104;u_lod_psd_kstellen_verteil;pnr_betriebliche#psd;kostenstelle#psd;prozentsatz_kst#psd;
                             105;u_lod_psd_ktraeger_verteil;pnr_betriebliche#psd;kostentraeger#psd;prozentsatz_ktr#psd;
                             200;u_lod_psd_mitarbeiter;pnr_betriebliche#psd;ersteintrittsdatum#psd;vorweg_abr_abruf_termin_kz#psd;
                             201;u_lod_psd_beschaeftigung;pnr_betriebliche#psd;eintrittdatum#psd;
                             240;u_lod_psd_festbezuege;pnr_betriebliche#psd;betrag#psd;festbez_id#psd;intervall#psd;kuerzung#psd;kz_monatslohn#psd;lohnart_nr#psd;
                             262;u_lod_psd_lohn_gehalt_bezuege;pnr_betriebliche#psd;std_lohn_1#psd;
                             287;u_lod_psd_sozialversicherung;pnr_betriebliche#psd;kk_nr#psd;av_bgrs#psd;kv_bgrs#psd;pv_bgrs#psd;rv_bgrs#psd;uml_schluessel#psd;
                             292;u_lod_psd_sv_unfall;pnr_betriebliche#psd;uv_kz_pflichtig#psd;uv_kz_stundenerm#psd;
                             300;u_lod_psd_taetigkeit;pnr_betriebliche#psd;persgrs#psd;berufsbezeichnung#psd;beschaeft_nr#psd;ausg_taetigkeit#psd;ausg_taetigkeit_lfdnr#psd;schulabschluss#psd;ausbildungsabschluss#psd;
                             400;u_lod_psd_taetigkeit;pnr_betriebliche#psd;arbeitnehmerueberlassung#psd;vertragsform#psd;rv_beitragsgruppe#psd;
                             503;u_lod_psd_taetigkeit;pnr_betriebliche#psd;stammkostenstelle#psd;
                             701;u_lod_psd_steuer;pnr_betriebliche#psd;st_klasse#psd;faktor#psd;kfb_anzahl#psd;els_2_haupt_ag_kz#psd;konf_an#psd;
                             702;u_lod_psd_steuer;pnr_betriebliche#psd;identifikationsnummer#psd;
                             800;u_lod_psd_arbeitszeit_regelm;pnr_betriebliche#psd;az_wtl_indiv#psd;regelm_az_mo#psd;regelm_az_di#psd;regelm_az_mi#psd;regelm_az_do#psd;regelm_az_fr#psd;regelm_az_sa#psd;regelm_az_so#psd;
                             801;u_lod_psd_arbeitszeit_regelm;pnr_betriebliche#psd;url_tage_jhrl#psd;


                             [Stammdaten]
                       """
        if len(template) == 0:
            raise Exception('Specificeer eerst een export template voordat u deze gebruikt!')

        return template

    def export_to_template(self, df: pd.DataFrame, valid_from: pd.datetime, use_alternative_employee_number=False):

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                return f'Column {field} is required. Required columns are: {tuple(required_fields)}'

        # This is the custom export that is different per customer. This one makes a txt for every new employee and adds information in the template with a string format.
        template = self.get_template(valid_from, use_alternative_employee_number)
        for index, dfrow in df.iterrows():
            with open('self.output_dir' + 'ANF_LuG_508701_28334_' + str(dfrow['employee_id']) + '.txt', 'w', encoding="latin-1", newline='\r\n') as file:
                lines = [template]
                #
                # """
                #              100;{employee_id};{lastname};{firstname};{birthname};{street};{housenumber};{postalcode};{city_of_residence};;;
                #              101;{employee_id};{date_of_birth};{place_of_birth};{country_of_birth};{gender};{social_security_number};{nationality};
                #              102;{employee_id};{iban};{iban_code};5;
                #              103;{employee_id};{disabled};{type_of_employee};
                #              104;{employee_id};{costcenter};{costcenter_percentage};
                #              105;{employee_id};{costcarrier};{costcarrier_percentage};
                #              200;{employee_id};{date_in_service};{payment_type};
                #              201;{employee_id};{first_day_of_employement};
                #              240;{employee_id};{amount};{tracking_number};{interval};{discount};{discount_monthly_salary};{wagecomponent_number};
                #              262;{employee_id};{hourly_wage};
                #              287;{employee_id};{insurancefund_number};{unemployment_insurance};{health_insurance};{healthcare_insurance};{pension_insurance};2;
                #              292;{employee_id};{mandatory_insurance};{hourly_wager};
                #              300;{employee_id};{person_group};{position};{place_of_work};{job_performed};{job_performed_description};{highest_degree};{highest_training};
                #              400;{employee_id};0;{type_of_contract};{employee_type};
                #              503;{employee_id};{costcenter};
                #              701;{employee_id};{tax_class};;;{main_employer};{religion};
                #              702;{employee_id};{taxnumber};
                #              800;{employee_id};{hours_per_week};{hours_monday};{hours_tuesday};{hours_wednesday};{hours_thursday};{hours_friday};{hours_saturday};{hours_sunday};
                #              801;{employee_id};{yearly_vacation_hours};
                # """
                required_columns_subset = ['lastname', 'firstname', 'birthname', 'street', 'housenumber', 'postalcode', 'city_of_residence']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"100;{dfrow['employee_id']};{dfrow['lastname']};{dfrow['firstname']};{dfrow['birthname']};{dfrow['street']};{dfrow['housenumber']};{dfrow['postalcode']};{dfrow['city_of_residence']};;;")

                required_columns_subset = ['date_of_birth', 'place_of_birth', 'country_of_birth', 'gender', 'social_security_number', 'nationality']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"101;{dfrow['employee_id']};{dfrow['date_of_birth']};{dfrow['place_of_birth']};{dfrow['country_of_birth']};{dfrow['gender']};{dfrow['social_security_number']};{dfrow['nationality']};")

                required_columns_subset = ['iban', 'iban_code']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"102;{dfrow['employee_id']};{dfrow['iban']};{dfrow['iban_code']};5;")

                required_columns_subset = ['disabled', 'type_of_employee']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"103;{dfrow['employee_id']};{dfrow['disabled']};{dfrow['type_of_employee']};")

                required_columns_subset = ['costcenter', 'costcenter_percentage']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"104;{dfrow['employee_id']};{dfrow['costcenter']};{dfrow['costcenter_percentage']};")
                lines.append(f"503;{dfrow['employee_id']};{dfrow['costcenter']};")

                required_columns_subset = ['costcarrier', 'costcarrier_percentage']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"105;{dfrow['employee_id']};{dfrow['costcarrier']};{dfrow['costcarrier_percentage']};")

                required_columns_subset = ['date_in_service', 'payment_type']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"200;{dfrow['employee_id']};{dfrow['date_in_service']};{dfrow['payment_type']};")

                required_columns_subset = ['first_day_of_employement']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"201;{dfrow['employee_id']};{dfrow['first_day_of_employement']};")

                required_columns_subset = ['amount', 'tracking_number', 'interval', 'discount', 'discount_monthly_salary', 'wagecomponent_number']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"240;{dfrow['employee_id']};{dfrow['amount']};{dfrow['tracking_number']};{dfrow['interval']};{dfrow['discount']};{dfrow['discount_monthly_salary']};{dfrow['wagecomponent_number']};")

                required_columns_subset = ['hourly_wage']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"262;{dfrow['employee_id']};{dfrow['hourly_wage']};")

                required_columns_subset = ['insurancefund_number', 'unemployment_insurance', 'health_insurance', 'healthcare_insurance', 'pension_insurance']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"287;{dfrow['employee_id']};{dfrow['insurancefund_number']};{dfrow['unemployment_insurance']};{dfrow['health_insurance']};{dfrow['healthcare_insurance']};{dfrow['pension_insurance']};2;")

                required_columns_subset = ['mandatory_insurance', 'hourly_wager']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"292;{dfrow['employee_id']};{dfrow['mandatory_insurance']};{dfrow['hourly_wager']};")

                required_columns_subset = ['person_group', 'position', 'place_of_work', 'job_performed', 'job_performed_description', 'highest_degree', 'highest_training']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"300;{dfrow['employee_id']};{dfrow['person_group']};{dfrow['position']};{dfrow['place_of_work']};{dfrow['job_performed']};{dfrow['job_performed_description']};{dfrow['highest_degree']};{dfrow['highest_training']};")

                required_columns_subset = ['type_of_contract', 'employee_type']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"400;{dfrow['employee_id']};0;{dfrow['type_of_contract']};{dfrow['employee_type']};")

                required_columns_subset = ['tax_class', 'main_employer', 'religion']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"701;{dfrow['employee_id']};{dfrow['tax_class']};;;{dfrow['main_employer']};{dfrow['religion']};")

                required_columns_subset = ['taxnumber']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"702;{dfrow['employee_id']};{dfrow['taxnumber']};")

                required_columns_subset = ['hours_per_week', 'hours_monday', 'hours_tuesday', 'hours_wednesday', 'hours_thursday', 'hours_friday', 'hours_saturday', 'hours_sunday']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"800;{dfrow['employee_id']};{dfrow['hours_per_week']};{dfrow['hours_monday']};{dfrow['hours_tuesday']};{dfrow['hours_wednesday']};{dfrow['hours_thursday']};{dfrow['hours_friday']};{dfrow['hours_saturday']};{dfrow['hours_sunday']};")

                required_columns_subset = ['yearly_vacation_hours']
                self.check_if_column_in_dataset(required_columns_subset, df.columns)
                lines.append(f"801;{dfrow['employee_id']};{dfrow['yearly_vacation_hours']};")

                file.writelines([])


    def check_if_column_in_dataset(self, required_columns_subset, df_columns):
        if any(column in required_columns_subset for column in df_columns):
            if not all(column in required_columns_subset for column in df_columns):
                raise Exception(f"You are missing one of the following columns : {','.join(required_columns_subset)}")
