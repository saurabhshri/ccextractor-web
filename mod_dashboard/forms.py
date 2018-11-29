"""
ccextractor-web | forms.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54+ccextractorweb[at]gmail.com
Link     : https://github.com/saurabhshri

"""
import os

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, TextAreaField, SelectField, BooleanField, StringField
from wtforms.validators import DataRequired, ValidationError


ALLOWED_EXTENSIONS = set(['.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d', '.787', '.89', '.aaf', '.aec', '.aep', '.aepx',
                          '.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim', '.aqt', '.arcut', '.arf', '.asf', '.asx', '.avb',
                          '.avc', '.avd', '.avi', '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3', '.bik', '.bin', '.bix',
                          '.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr', '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel', '.cine', '.cip',
                          '.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc', '.cx3', '.d2v', '.d3v', '.dat', '.dav', '.dce',
                          '.dck', '.dcr', '.dcr', '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d', '.dmsm', '.dmsm3d', '.dmss',
                          '.dmx', '.dnc', '.dpa', '.dpg', '.dream', '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms', '.dvx', '.dxr',
                          '.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p', '.f4v', '.fbr', '.fbr', '.fbz', '.fcp', '.fcproject',
                          '.ffd', '.flc', '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts', '.gvi', '.gvp', '.h264', '.hdmov',
                          '.hkm', '.ifo', '.imovieproj', '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva', '.ivf', '.ivr', '.ivs',
                          '.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g', '.kmv', '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg', '.m1v', '.m21',
                          '.m21', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75', '.mani', '.meta', '.mgv', '.mj2', '.mjp',
                          '.mjpg', '.mk3d', '.mkv', '.mmv', '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov', '.movie', '.mp21',
                          '.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg4', '.mpf', '.mpg', '.mpg2', '.mpgindex', '.mpl',
                          '.mpl', '.mpls', '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm', '.mts', '.mtv', '.mvb', '.mvc',
                          '.mvd', '.mve', '.mvex', '.mvp', '.mvp', '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv', '.nvc', '.ogm',
                          '.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi', '.photoshow', '.piv', '.pjs', '.playlist', '.plproj',
                          '.pmf', '.pmv', '.pns', '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd', '.pva', '.pvr', '.pxv',
                          '.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d', '.rcd', '.rcproject', '.rdb', '.rec', '.rm', '.rmd', '.rmd',
                          '.rmp', '.rms', '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv', '.rvid', '.rvl', '.sbk', '.sbt',
                          '.scc', '.scm', '.scm', '.scn', '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv', '.smi', '.smi',
                          '.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt', '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi', '.swf', '.swi',
                          '.swt', '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd', '.tpr', '.trp', '.ts', '.tsp', '.ttxt',
                          '.tvs', '.usf', '.usm', '.vc1', '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg', '.vem', '.vep', '.vf', '.vft',
                          '.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet', '.viv', '.vivo', '.vlab', '.vob', '.vp3', '.vp6', '.vp7', '.vpj',
                          '.vro', '.vs4', '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp', '.wmv', '.wmx', '.wot', '.wp3',
                          '.wpl', '.wtv', '.wve', '.wvx', '.xej', '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog', '.yuv', '.zeg',
                          '.zm1', '.zm2', '.zm3', '.zmv', 'bin', 'raw'])


class UploadForm(FlaskForm):
    accept = 'video/mp4, video/x-m4v, video/*, .bin, .raw, video/MP2T, .ts'

    file = FileField('Select your file', [DataRequired(message='No file selected.')], render_kw={'accept': accept})

    parameters = TextAreaField('Parameters')
    ccextractor_version = SelectField('CCExtractor Version', [DataRequired(message='Select Version')], coerce=str)
    platforms = SelectField('Platform', [DataRequired(message='Select platform')], coerce=str)
    remark = TextAreaField('Remarks')
    start_processing = BooleanField('Start Processing', default=True)
    submit = SubmitField('Upload file')

    @staticmethod
    def validate_file(form, field):
        filename, extension = os.path.splitext(field.data.filename)
        if len(extension) > 0:
            if extension not in ALLOWED_EXTENSIONS:  # or guessed_extension not in ALLOWED_EXTENSIONS:
                raise ValidationError('Extension not allowed')


class NewJobForm(FlaskForm):
    parameters = TextAreaField('Parameters')
    ccextractor_version = SelectField('CCExtractor Version', [DataRequired(message='Select Version')], coerce=str)
    platforms = SelectField('Platform', [DataRequired(message='Select platform')], coerce=str)
    remark = TextAreaField('Remarks')
    submit = SubmitField('Submit')


class NewCCExtractorVersionForm(FlaskForm):
    version = StringField('Version', [DataRequired(message='Version is not filled in.')])
    commit = StringField('Commit', [DataRequired(message='Commit is not filled in.')])
    linux_executable_path = StringField('Path to Linux executable file')
    windows_executable_path = StringField('Path to Windows executable file')
    mac_executable_path = StringField('Path to macOS executable file')
    submit = SubmitField('Add')


class NewCCExtractorParameterForm(FlaskForm):
    parameter = StringField('parameter', [DataRequired(message='Parameter is not filled in.')])
    description = StringField('Description', [DataRequired(message='Description is not filled in.')])
    requires_value = BooleanField('Requires Value?')
    enabled = BooleanField('Enable this parameter?', default=True)
    submit = SubmitField('Submit')
