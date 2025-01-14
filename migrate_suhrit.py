import json
import io
from datetime import datetime, date


def get_db():
    from pymongo import MongoClient
    return MongoClient('mongodb+srv://vin:Ww8tw2wutr02krWY@cluster0.sgu0rat.mongodb.net/')


def copy_counts(db, sdb):

    for count_item in db.counts.find({}):
        count_item['tenantId'] = 1
        del count_item["_id"]
        print(count_item)
        sdb.counts.insert_one(count_item)


def convert_profile(profile):
    mig_prof = {}
    if 'curMedcine' in profile.keys():
        mig_prof['curMedcine'] = profile['curMedcine']

    if 'reason' in profile.keys():
        mig_prof['reason'] = profile['reason']

    if 'diagnosis' in profile.keys():
        mig_prof['diagnosis'] = profile['diagnosis']

    if 'tags' in profile.keys():
        mtags = []
        for tag in profile['tags']:
            mtags.append(tag['display'])
        mig_prof['tags'] = mtags

    history = ['हृदय रोग', 'अनूर्जता', 'अर्श', 'धूम्रपान',
               'मद्यपान', 'औषध', 'गुटका', 'तम्बाकू', 'माँसाहारी']
    mhist = []
    for hist in history:
        if hist in profile.keys():
            if profile[hist] == True:
                mhist.append(hist)
    mig_prof['history'] = mhist

    readings = ['मधुमेह', 'रक्तचाप', 'लक्षण/चिन्ह',
                'प्रयोगशाला संबंधी', 'पूर्व निदान', 'उपद्रव', 'Weight']
    mread = {}
    for read in readings:
        if read in profile.keys():
            mread[read] = profile[read]
    mig_prof['readings'] = mread

    exams = ['भूख', 'शौच', 'मूत्र', 'निद्रा', 'चयापचय स्थिति', 'प्रकृति', 'नेत्र',
             'जीभ', 'आकृति', 'नाभिस्थिति', 'दाईं नाड़ी', 'बाईं नाड़ी', 'मासिक धर्म']
    mexam = {}
    for exam in exams:
        if exam in profile.keys():
            mexam[exam] = profile[exam]

    mig_prof['exams'] = mexam
    return mig_prof


def convert_diet(diet):
    pathya = []
    apathya = []
    for d in diet.keys():
        if diet[d] == "1":
            pathya.append(d)
        else:
            apathya.append(d)

    return pathya, apathya


def copy_history(db, sdb, patients):
    print("*****copy_history******")
    count = 0 
    records = []
    for pid in patients:
        # print(pid)
        history = db.history.find_one({'patientId': pid})
        mvisits = []
        mhist = {'patientId': history['patientId'], 'tenantId': 1}
        for vis in history['visits']:
            mvis = {}
            mvis['type'] = 'OPD'
            mvis['visitId'] = vis['visitId']
            mvis['visitDate'] = datetime.strptime(vis['visitDate'], "%Y-%m-%d")
            mvis['opdPayment'] = vis['opdPayment']
            mvis['profile'] = convert_profile(vis['profile'])
            mvis['aasans'] = []
            for aasan in vis['aasans']:
                if vis['aasans'][aasan]:
                    # print(vis['aasans'][aasan])
                    mvis['aasans'].append(aasan)

            mvis['karms'] = []
            for karm in vis['karms']:
                if vis['karms'][karm]:
                    # print(vis['aasans'][aasan])
                    mvis['karms'].append(karm)
            mvis['medicines'] = vis['medicines']
            pathya, apathya = convert_diet(vis['pdiet'])
            mvis['pathya'] = pathya
            mvis['apathya'] = apathya
            mvisits.insert(0, mvis)

        mkvisits = []
        if 'kvisits' in history.keys():
            for vis in history['kvisits']:
                mkvis = {}
                mkvis['type'] = 'Karm'
                mkvis['kvisitId'] = vis['kvisitId']
                mkvis['visitDate'] = datetime.strptime(
                    vis['visitDate'], "%Y-%m-%d")
                mkvis['payment'] = vis['payment']
                if isinstance(vis['karms'], list):
                    mkarms = {}
                    for item in vis['karms']:
                        mkarms.update(item)
                    mkvis['karms'] = mkarms
                else:
                    mkvis['karms'] = vis['karms']
                mkvisits.insert(0, mkvis)

        mhist['visits'] = mvisits
        mhist['kvisits'] = mkvisits
        count += 1
        records.append(mhist)
        if count % 25 == 0:
            print(pid)
            sdb.history.insert_many(records)
            records =  []
            count = 0
        # sdb.history.insert_one(mhist)
    if count > 0:
        print(pid)
        sdb.history.insert_many(records)

def copy_patients(db, sdb, patients):
    print("*****copy_patients******")
    count = 0 
    records = []
    for pid in patients:
        # print(pid)
        patient = db.patient.find_one({'patientId': pid})
        patient['dateofbirth'] = datetime.strptime(
            patient['dateofbirth'], "%Y-%m-%d")
        del patient['_id']
        patient['tenantId'] = 1
        count += 1
        records.append(patient)
        if count % 100 == 0:
            print(pid)
            sdb.patients.insert_many(records)
            records =  []
            count = 0
        # sdb.patients.insert_one(patient)
    if count > 0:
        print(pid)
        sdb.patients.insert_many(records)

def clean_collections(sdb):
    print("*****clean_collections******")
    sdb.counts.delete_many({})
    sdb.history.delete_many({})
    sdb.patients.delete_many({})


def migrate():
    client = get_db()
    db = client.drdigi
    sdb = client['suhrit-prod']

    proc_patients = [6575]
    # patients = []
    # for item in db.history.find({}, {'patientId': 1, '_id': 0}).to_list():
    #     patients.append(item['patientId'])
    # # print(patients)
    # proc_patients = []
    # for i in range(5700,8100):
    #     if i in patients:
    #         proc_patients.append(i)
    # # for item in db.history.find().sort('patientId':1):
    # #     patients.append(item['patientId'])

    # clean_collections(sdb)
    # copy_counts(db, sdb)
    copy_patients(db, sdb, proc_patients)
    copy_history(db, sdb, proc_patients)
    print(sdb.patients.count_documents({}))
    print(sdb.history.count_documents({}))


if __name__ == '__main__':
    migrate()
