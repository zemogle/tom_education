from datetime import datetime
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.mail import send_mass_mail
from django.template import loader, Context
import glob
import json
import logging
import os
import requests
import subprocess

from tom_observations.facility import get_service_class
from tom_observations.models import ObservationRecord
from tom_dataproducts.models import DataProduct

from tom_education.models import Target, TimeLapse

logger = logging.getLogger('__name__')


def set_update_time(date_obs, last_update):
    date_obs, _, us = date_obs.partition(".")
    tmp_date = datetime.strptime(date_obs, "%Y-%m-%dT%H:%M:%S")
    if tmp_date > last_update:
        last_update = tmp_date
    return last_update, tmp_date

def save_reduced_lco_dataproducts(target_id):
    '''
    target_id: unique ID of the target to look up
    '''
    obs_recs = ObservationRecord.objects.filter(target__identifier=target_id)
    if not obs_recs:
        return False
    service_class = get_service_class(obs_recs[0].facility)
    reduced_products = []
    for obs_rec in obs_recs:
        products = service_class().all_data_products(obs_rec)
        # Only save the reduced files
        for product in products['unsaved']:
            if 'e91' in product['filename']:
                p = service_class().save_data_products(obs_rec, product['id'])
                reduced_products.append(p)
    logger.debug('Successfully saved: {0}'.format('\n'.join([str(p) for p in reduced_products])))
    return

def find_saved_data_products(target_id):
    '''
    target_id: unique ID of the target to look up
    '''
    obs_recs = ObservationRecord.objects.filter(target__identifier=target_id)
    frames = []
    for obs_rec in obs_recs:
        products = get_service_class(obs_rec.facility)().all_data_products(obs_rec)
        frames.append(products['saved'])
    logger.debug("Total frames=%s" % (len(frames)))
    return frames

def fits_jpegs(frames):

    return

def make_timelapse(target_name, files, format="mp4"):
    logger.debug('Making {} timelapse for {}'.format(format, target_name))
    if files:
        if format == 'mp4':
            outfile = '{}.mp4'.format(target_name.replace(" ", ""))
            outfile = os.path.join(file_dir, outfile)
            video_options = "ffmpeg -framerate 10 -pattern_type glob -i '{}' -vf 'scale=2*iw:-1, crop=iw/2:ih/2' -s 696x520 -vcodec libx264 -f mp4 -pix_fmt yuv420p {} -y".format(path, outfile)
        elif format == 'webm':
            outfile = '{}.webm'.format(target_name.replace(" ", ""))
            outfile = os.path.join(file_dir, outfile)
            video_options = "ffmpeg -framerate 10 -pattern_type glob -i '{}' -vf 'scale=2*iw:-1, crop=iw/2:ih/2' -s 696x520 -vcodec libvpx-vp9 -f webm {} -y".format(path, outfile)

        try:
            output = subprocess.check_output(video_options, stderr=subprocess.STDOUT, shell=True, timeout=30, universal_newlines=True)
        except subprocess.CalledProcessError as exc:
            logger.error("FAILED {}".format(exc.output))
        else:
            logger.debug("Successfully created {}".format(outfile))
            return outfile
    return False


def timelapse_overseer(tl_id, dir):
    '''
    Function to find and download image files, then create new timelapse and append
    to old timelapse

    target_id: int
        PK of target object
    dir: str
        Directory to download all files into
    '''
    tl = TimeLapse.objects.get(pk=tl_id)
    frames, last_update = find_frames_object(tl.target)
    for format in (('mp4','timelapse_mpeg'), ('webm','timelapse_webm')):
        outfile = make_timelapse(tl.target.name, dir, format=format[0])
        if outfile:
            if getattr(tl,format[1]):
                oldtimelapse = download_timelapse(filename=getattr(tl,format[1]), download_dir=dir, format=format[0])
                outfile = combine_timelapses(dir, outfile, format[0])
            outfile_name = os.path.basename(outfile)
            with open(outfile, 'rb') as f:
                if format[0] == 'mp4':
                    tl.timelapse_mpeg.save(outfile_name, File(f), save=True)
                if format[0] == 'webm':
                    tl.timelapse_webm.save(outfile_name, File(f), save=True)
            tl.last_update = last_update
            tl.num_observations += len(glob.glob(dir+'*.jpg'))
            tl.save()
    return
