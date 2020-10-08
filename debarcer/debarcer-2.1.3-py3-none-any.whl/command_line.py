# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 16:46:05 2020

@author: rjovelin
"""

import argparse
from debarcer import preprocess_reads, group_umis, collapse, VCF_converter, \
merge_files, run_scripts, generate_figures, report, generate_bed
from src.utilities import ConvertArgToBool

def main():
    
    ## Argument + config parsing and error handling
    parser = argparse.ArgumentParser(prog='debarcer.py', description="A package for De-Barcoding\
                                     and Error Correction of sequencing data containing molecular barcodes")
    subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')
    
    ## Preprocess command
    p_parser = subparsers.add_parser('preprocess', help="Preprocess mode for processing fastq files")
    p_parser.add_argument('-o', '--OutDir', dest='outdir', help='Output directory. Available from command or config')
    p_parser.add_argument('-r1', '--Read1', dest='read1', help='Path to first FASTQ file.', required=True)
    p_parser.add_argument('-r2', '--Read2', dest='read2', help='Path to second FASTQ file, if applicable')
    p_parser.add_argument('-r3', '--Read3', dest='read3', help='Path to third FASTQ file, if applicable')
    p_parser.add_argument('-p', '--Prepname', dest='prepname', choices=['HALOPLEX', 'SURESELECT', 'EPIC-DS', 'SIMSENSEQ-PE', 'SIMSENSEQ-SE'], 
                          help='Name of library prep to  use (defined in library_prep_types.ini)', required=True)
    p_parser.add_argument('-pf', '--Prepfile', dest='prepfile', help='Path to your library_prep_types.ini file')
    p_parser.add_argument('-c', '--Config', dest='config', help='Path to your config file')
    p_parser.add_argument('-px', '--Prefix', dest= 'prefix', help='Prefix for naming umi-reheradered fastqs. Use Prefix from Read1 if not provided') 
        
    ## Bed command
    b_parser = subparsers.add_parser('bed', help='Generate a bed file by scanning input bam for regions of coverage')
    b_parser.add_argument('-b', '--Bamfile', dest='bamfile', help='Path to the BAM file', required=True)
    b_parser.add_argument('-bd', '--Bedfile', dest='bed', help='Path to the output bed file', required=True)
    b_parser.add_argument('-mv', '--MinCov', dest='mincov', type=int, help='Minimum read depth value at all positions in genomic interval', required=True)
    b_parser.add_argument('-r', '--RegionSize', dest='regionsize', type=int, help='Minimum length of the genomic interval (in bp)', required=True)
    b_parser.add_argument('-m', '--MaxDepth', dest='maxdepth', default=1000000, type=int, help='Maximum read depth. Default is 1000000')
    b_parser.add_argument('-io', '--IgnoreOrphans', dest='ignoreorphans', action='store_true', help='Ignore orphans (paired reads that are not in a proper pair). Default is False, becomes True if used')
    b_parser.add_argument('-stp', '--Stepper', dest='stepper', choices=['all', 'nofilter'], default='nofilter',
                          help='Filter or include reads in the pileup. Options all: skip reads with BAM_FUNMAP, BAM_FSECONDARY, BAM_FQCFAIL, BAM_FDUP flags,\
                          nofilter: uses every single read turning off any filtering')
        
    ## UMI group command
    g_parser = subparsers.add_parser('group', help="Groups UMIs into families.")
    g_parser.add_argument('-o', '--Outdir', dest='outdir', help='Output directory where subdirectories are created')
    g_parser.add_argument('-r', '--Region', dest='region', help='Region coordinates to search for UMIs. chrN:posA-posB. posA and posB are 1-based included', required=True)
    g_parser.add_argument('-b', '--Bamfile', dest='bamfile', help='Path to the BAM file')
    g_parser.add_argument('-c', '--Config', dest='config', help='Path to the config file')
    g_parser.add_argument('-d', '--Distance', dest='distthreshold', type=int, help='Hamming distance threshold for connecting parent-children umis')
    g_parser.add_argument('-p', '--Position', dest='postthreshold', type=int, help='Umi position threshold for grouping umis together')
    g_parser.add_argument('-i', '--Ignore', dest='ignore', choices=[True, False], type=ConvertArgToBool, default=False, help='Keep the most abundant family and ignore families at other positions within each group. Default is False')
    g_parser.add_argument('-t', '--Truncate', dest='truncate', choices=[True, False], default=False, type=ConvertArgToBool, help='Discard reads overlapping with the genomic region if True. Default is False')
    g_parser.add_argument('-s', '--Separator', dest='separator', default=':', help = 'String separating the UMI from the remaining of the read name')
    g_parser.add_argument('-rc', '--ReadCount', dest='readcount', default=0, type=int, help = 'Minimum number of reads in region required for grouping. Default is 0')
        
    ## Base collapse command
    c_parser = subparsers.add_parser('collapse', help="Base collapsing from given UMI families file.")
    c_parser.add_argument('-c', '--Config', dest='config', help='Path to the config file')
    c_parser.add_argument('-o', '--Outdir', dest='outdir', help='Output directory where subdirectories are created')
    c_parser.add_argument('-b', '--Bamfile', dest='bamfile', help='Path to the BAM file')
    c_parser.add_argument('-rf', '--Reference', dest='reference', help='Path to the refeence genome')
    c_parser.add_argument('-r', '--Region', dest='region', help='Region coordinates to search for UMIs. chrN:posA-posB. posA and posB are 1-based included', required=True)
    c_parser.add_argument('-u', '--Umi', dest='umifile', help='Path to the .umis file', required=True)
    c_parser.add_argument('-f', '--Famsize', dest='famsize', help='Comma-separated list of minimum umi family size to collapase on')
    c_parser.add_argument('-ct', '--CountThreshold', dest='countthreshold', type=int, help='Base count threshold in pileup column')
    c_parser.add_argument('-pt', '--PercentThreshold', dest='percentthreshold', type=float, help='Majority rule consensus threshold in pileup column')
    c_parser.add_argument('-p', '--Position', dest='postthreshold', type=int, help='Umi position threshold for grouping umis together')
    c_parser.add_argument('-m', '--MaxDepth', dest='maxdepth', default=1000000, type=int, help='Maximum read depth. Default is 1000000')
    c_parser.add_argument('-t', '--Truncate', dest='truncate', choices=[True, False], default=False, type=ConvertArgToBool, help='If truncate is True and a region is given,\
                          only pileup columns in the exact region specificied are returned. Default is False')
    c_parser.add_argument('-i', '--IgnoreOrphans', dest='ignoreorphans', choices=[True, False], default=False, type=ConvertArgToBool, help='Ignore orphans (paired reads that are not in a proper pair). Default is False')
    c_parser.add_argument('-stp', '--Stepper', dest='stepper', choices=['all', 'nofilter'], default='nofilter',
                          help='Filter or include reads in the pileup. Options all: skip reads with BAM_FUNMAP, BAM_FSECONDARY, BAM_FQCFAIL, BAM_FDUP flags,\
                          nofilter: uses every single read turning off any filtering')
    c_parser.add_argument('-s', '--Separator', dest='separator', default=':', help = 'String separating the UMI from the remaining of the read name')
    c_parser.add_argument('-bq', '--Quality', dest='base_quality_score', type=int, default=25, help = 'Base quality score threshold. Bases with quality scores below the threshold are not used in the consensus. Default is 25')
    
    ## Variant call command - requires cons file (can only run after collapse)
    v_parser = subparsers.add_parser('call', help="Convert consensus file into VCF format.")
    v_parser.add_argument('-o', '--Outdir', dest='outdir', help='Output directory where subdirectories are created')
    v_parser.add_argument('-c', '--Config', dest='config', help='Path to the config file')
    v_parser.add_argument('-rf', '--Reference', dest='reference', help='Path to the refeence genome')
    v_parser.add_argument('-rt', '--RefThreshold', dest='refthreshold', default=95, type=float, 
                          help='Maximum reference frequency to consider (in percent) alternative variants\
                          (ie. position with ref freq <= ref_threshold is considered variable)')
    v_parser.add_argument('-at', '--AlternativeThreshold', dest='altthreshold', type=float, default=2,
                          help='Minimum allele frequency (in percent) to consider an alternative allele at a variable position\
                          (ie. allele freq >= alt_threshold and ref freq <= ref_threshold: alternative allele)')
    v_parser.add_argument('-ft', '--FilterThreshold', dest='filterthreshold', type=int, default=10,
                          help='Minimum number of reads to pass alternative variants\
                          (ie. filter = PASS if variant depth >= alt_threshold)')
    v_parser.add_argument('-f', '--Famsize', dest='famsize', type=int, help='Minimum UMI family size', required=True)
        
    ## Run scripts command 
    r_parser = subparsers.add_parser('run', help="Generate scripts for umi grouping, collapsing and VCF formatting for target regions specified by the BED file.")
    r_parser.add_argument('-o', '--Outdir', dest='outdir', help='Output directory where subdirectories are created')
    r_parser.add_argument('-c', '--Config', dest='config', help='Path to the config file')
    r_parser.add_argument('-b', '--Bamfile', dest='bamfile', help='Path to the BAM file')
    r_parser.add_argument('-rf', '--Reference', dest='reference', help='Path to the refeence genome')
    r_parser.add_argument('-f', '--Famsize', dest='famsize', help='Comma-separated list of minimum umi family size to collapase on')
    r_parser.add_argument('-bd', '--Bedfile', dest='bedfile', help='Path to the bed file', required=True)
    r_parser.add_argument('-ct', '--CountThreshold', dest='countthreshold', type=int, help='Base count threshold in pileup column')
    r_parser.add_argument('-pt', '--PercentThreshold', dest='percentthreshold', type=float, help='Base percent threshold in pileup column')
    r_parser.add_argument('-p', '--Position', dest='postthreshold', type=int, help='Umi position threshold for grouping umis together')
    r_parser.add_argument('-d', '--Distance', dest='distthreshold', type=int, help='Hamming distance threshold for connecting parent-children umis')
    r_parser.add_argument('-rt', '--RefThreshold', dest='refthreshold', default=95, type=float, help='A position is considered variable of reference frequency is <= ref_threshold')
    r_parser.add_argument('-at', '--AlternativeThreshold', dest='altthreshold', default=2, type=float, help='Variable position is labeled PASS if allele frequency >= alt_threshold')
    r_parser.add_argument('-ft', '--FilterThreshold', dest='filterthreshold', default=10, type=int, help='Minimum number of reads to pass alternative variants')
    r_parser.add_argument('-m', '--MaxDepth', dest='maxdepth', default=1000000, type=int, help='Maximum read depth. Default is 1000000')
    r_parser.add_argument('-t', '--Truncate', dest='truncate', action='store_true', help='Only pileup columns in the exact region specificied are returned. Default is False, becomes True is used')
    r_parser.add_argument('-io', '--IgnoreOrphans', dest='ignoreorphans', action='store_true', help='Ignore orphans (paired reads that are not in a proper pair). Default is False, becomes True if used')
    r_parser.add_argument('-i', '--Ignore', dest='ignore', action='store_true', help='Keep the most abundant family and ignore families at other positions within each group. Default is False, becomes True if used')
    r_parser.add_argument('-mg', '--Merge', dest='merge', action='store_false', help='Merge data, json and consensus files respectively into a 1 single file. Default is True, becomes False if used')
    r_parser.add_argument('-pl', '--Plot', dest='plot',  action='store_false', help='Generate figure plots. Default is True, becomes False if used')
    r_parser.add_argument('-rp', '--Report', dest='report', action='store_false', help='Generate report. Default is True, becomes False if used')
    r_parser.add_argument('-cl', '--Call', dest='call', action='store_false', help='Convert consensus files to VCF format. Default is True, becomes False if used')
    r_parser.add_argument('-ex', '--Extension', dest='extension', choices=['png', 'jpeg', 'pdf'], default='png', help='Figure format. Does not generate a report if pdf, even with -r True. Default is png')
    r_parser.add_argument('-sp', '--Sample', dest='sample', help='Sample name to appear to report. Optional, use Output directory basename if not provided')
    r_parser.add_argument('-pr', '--Project', dest='project', default='gsi', help='Project for submitting jobs on Univa')
    r_parser.add_argument('-mm', '--Memory', dest='mem', default=20, type=int, help='Requested memory for submitting jobs to SGE. Default is 20g')
    r_parser.add_argument('-py', '--MyPython', dest='mypython', default='/.mounts/labs/PDE/Modules/sw/python/Python-3.6.4/bin/python3.6',
                          help='Path to python. Default is /.mounts/labs/PDE/Modules/sw/python/Python-3.6.4/bin/python3.6')
    r_parser.add_argument('-db', '--MyDebarcer', dest='mydebarcer', default='/.mounts/labs/PDE/Modules/sw/python/Python-3.6.4/lib/python3.6/site-packages/debarcer/debarcer.py',
                          help='Path to the file debarcer.py. Default is /.mounts/labs/PDE/Modules/sw/python/Python-3.6.4/lib/python3.6/site-packages/debarcer/debarcer.py')
    r_parser.add_argument('-mv', '--MinCov', dest='mincov', type=int, default=1000, help='Minimum coverage value. Values below are plotted in red')
    r_parser.add_argument('-mr', '--MinRatio', dest='minratio', type=float, default=0.1, help='Minimum children to parent umi ratio. Values below are plotted in red')
    r_parser.add_argument('-mu', '--MinUmis', dest='minumis', type=int, default=1000, help='Minimum umi count. Values below are plotted in red')
    r_parser.add_argument('-mc', '--MinChildren', dest='minchildren', type=int, default=500, help='Minimum children umi count. Values below are plotted in red')
    r_parser.add_argument('-stp', '--Stepper', dest='stepper', choices=['all', 'nofilter'], default='nofilter',
                          help='Filter or include reads in the pileup. Options all: skip reads with BAM_FUNMAP, BAM_FSECONDARY, BAM_FQCFAIL, BAM_FDUP flags,\
                          nofilter: uses every single read turning off any filtering')
    r_parser.add_argument('-s', '--Separator', dest='separator', default=':', help = 'String separating the UMI from the remaining of the read name')
    r_parser.add_argument('-bq', '--Quality', dest='base_quality_score', type=int, default=25, help = 'Base quality score threshold. Bases with quality scores below the threshold are not used in the consensus. Default is 25')
    r_parser.add_argument('-rc', '--ReadCount', dest='readcount', default=0, type=int, help = 'Minimum number of reads in region required for grouping. Default is 0')
        
    ## Merge files command 
    m_parser = subparsers.add_parser('merge', help="Merge files from each region into a single file")
    m_parser.add_argument('-d', '--Directory', dest='directory', help='Directory containing files to be merged')
    m_parser.add_argument('-dt', '--DataType', dest='datatype', choices=['datafiles', 'consensusfiles', 'umifiles'], help='Type of files to be merged', required=True)
        
    ## Generate graphs	
    plot_parser = subparsers.add_parser('plot', help="Generate graphs for umi and cons data files", add_help=True)
    plot_parser.add_argument('-c', '--Config', dest='config', help='Path to the config file')
    plot_parser.add_argument('-d', '--Directory', dest='directory', help='Directory with subdirectories ConsFiles and Datafiles', required=True)
    plot_parser.add_argument('-e', '--Extension', dest='extension', default='png', choices=['pdf', 'png', 'jpeg'], help='Figure format. Does not generate a report if pdf, even with -r True. Default is png')
    plot_parser.add_argument('-s', '--Sample', dest='sample', help='Sample name to apear in the report is reporting flag activated. Optional')
    plot_parser.add_argument('-r', '--Report', dest='report', choices=[False, True], type=ConvertArgToBool, default=True, help='Generate a report if activated. Default is True')
    plot_parser.add_argument('-mv', '--MinCov', dest='mincov', type=int, default=1000, help='Minimum coverage value. Values below are plotted in red')
    plot_parser.add_argument('-mr', '--MinRatio', dest='minratio', type=float, default=0.1, help='Minimum children to parent umi ratio. Values below are plotted in red')
    plot_parser.add_argument('-mu', '--MinUmis', dest='minumis', type=int, default=1000, help='Minimum umi count. Values below are plotted in red')
    plot_parser.add_argument('-mc', '--MinChildren', dest='minchildren', type=int, default=500, help='Minimum children umi count. Values below are plotted in red')
    plot_parser.add_argument('-rt', '--RefThreshold', dest='refthreshold', default=95, type=float, help='Cut Y axis at non-ref frequency, the minimum frequency to consider a position variable')
        
    ## Generate report
    report_parser = subparsers.add_parser('report', help="Generate report", add_help=True)
    report_parser.add_argument('-d', '--Directory', dest='directory', help='Directory with subdirectories including Figures', required=True)
    report_parser.add_argument('-e', '--Extension', dest='extension', default='png', choices=['pdf', 'png', 'jpeg'], help='Figure format. Does not generate a report if pdf, even with -r True. Default is png')
    report_parser.add_argument('-s', '--Sample', dest='sample', help='Sample name. Optional. Directory basename is sample name if not provided')
    report_parser.add_argument('-mv', '--MinCov', dest='mincov', type=int, default=1000, help='Minimum coverage value. Values below are plotted in red')
    report_parser.add_argument('-mr', '--MinRatio', dest='minratio', type=float, default=0.1, help='Minimum children to parent umi ratio. Values below are plotted in red')
    report_parser.add_argument('-mu', '--MinUmis', dest='minumis', type=int, default=1000, help='Minimum umi count. Values below are plotted in red')
    report_parser.add_argument('-mc', '--MinChildren', dest='minchildren', type=int, default=500, help='Minimum children umi count. Values below are plotted in red')
    
        
    args = parser.parse_args()
    
    
    if args.subparser_name == 'preprocess':
        try:
            preprocess_reads(args.outdir, args.read1, args.read2, args.read3, args.prepname, args.prepfile, args.config, args.prefix)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'bed':
        try:
            generate_bed(args.bamfile, args.bed, args.contig, args.mincov, args.regionsize, args.maxdepth, args.ignoreorphans, args.stepper)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'group':
        try:
            group_umis(args.outdir, args.region, args.bamfile, args.config, args.distthreshold, args.postthreshold, args.ignore, args.truncate, args.separator, args.readcount)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'collapse':
        try:
            collapse(args.config, args.outdir, args.bamfile, args.reference, args.region,
                     args.umifile, args.famsize, args.countthreshold, args.percentthreshold,
                     args.postthreshold, args.maxdepth, args.truncate, args.ignoreorphans, 
                     args.stepper, args.separator, args.base_quality_score)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'call':
        try:
            VCF_converter(args.config, args.outdir, args.reference, args.refthreshold, args.altthreshold, args.filterthreshold, args.famsize)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'run':
        try:
            run_scripts(args.outdir, args.config, args.bamfile, args.reference,
                        args.famsize, args.bedfile, args.countthreshold, args.consensusthreshold,
                        args.postthreshold, args.distthreshold, args.refthreshold,
                        args.altthreshold, args.filterthreshold, args.percentthreshold, args.maxdepth,
                        args.truncate, args.ignoreorphans, args.ignore, args.stepper,
                        args.merge, args.plot, args.report, args.call, args.mincov,
                        args.minratio, args.minumis, args.minchildren, args.extension,
                        args.sample, args.mem, args.mypython, args.mydebarcer, args.project,
                        args.separator, args.base_quality_score, args.readcount)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'merge':
        try:
            merge_files(args.directory, args.datatype)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'plot':
        try:
            generate_figures(args.directory, args.config, args.extension, args.report, args.sample, args.mincov, args.minratio, args.minumis, args.minchildren, args.refthreshold)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name == 'report':
        try:
            report(args.directory, args.extension, args.mincov, args.minratio, args.minumis, args.minchildren, sample=args.sample)
        except AttributeError as e:
            print('AttributeError: {0}\n'.format(e))
            print(parser.format_help())
    elif args.subparser_name is None:
        print(parser.format_help())