# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
ids=local_import('set_ids')
cats=local_import('catFun')
st=local_import('saveTweets')
snd=local_import('sendMail')
chk=local_import('verifyMail')
city=local_import('states')
rnk=local_import('ranking')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
def stackrank():
    #r_tb=db().select(db.Rankings)
    return locals()

def sendMailToCollege(pp):
     for probs in db(db.Problems.id==pp).select(db.Problems.p_loc):
            for emails in db(db.Colleges.c_loc==probs.p_loc).select(db.Colleges.c_email):
                snd.send(emails.c_email,pp)
def checkMail(form):
    emailid=form.vars.p_userid
    if chk.check_mail(emailid):
        return
    else:
        form.errors.p_userid = 'Invalid Email Address,please check your email address'
def validate(form):
    pid=form.vars.id
    emailid=form.vars.contact
    if db(db.Problems.id==pid).count()==0:
        form.errors.p_id="Invalid problem id.Problem doesn't exist in the database"
    emailid=form.vars.contact
    if chk.check_mail(emailid):
        return
    else:
        form.errors.contact = 'Invalid Email Address,please check your email address'


@auth.requires_login()
def upload_sol():

    form=SQLFORM(db.Solutions)
    if form.process().accepted: #onvalidation=validate
        response.flash='Thank You, Your Solution Has Been Successfully Submitted'
        redirect(URL(r=request,f='index'))
    elif form.errors:
        response.flash='Please Check The Form Again'
    else:
        response.flash='Upload Your Solution'
    return dict(form=form)
def view_prob():
    idss=request.get_vars
    prob=db(db.Problems.id==idss).select()
    return idss
def Browse_problem():
    if auth.user_id!=None:
        locs = db(db.auth_user.id == auth.user_id).select(db.auth_user.Loc).first()
    export_classes = dict(csv=True, json=True, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    prob=db(db.Problems).select()
    links = [

    lambda row: A(TAG[''](SPAN(_class="icon icon-user"),SPAN('Claim', _class="btn btn-primary", _title="Claim")), _class="w2p_trap button btn", _href=URL('upload_sol', args=[row.id])),  lambda row: A(TAG[''](SPAN(_class="icon icon-user"),SPAN('Realted Solutions', _class="btn btn-danger", _title="Related Solutions")), _class="w2p_trap button btn", _href=URL('relatedsolution',args=[row.id]))]

    fields = (db.Problems.id,db.Problems.p_loc, db.Problems.p_text,db.Problems.p_category,db.Problems.p_status)
    headers = {'Problems.id':'PID',
           'Problems.p_userid': 'Email Id',
           'Problems.p_loc':'Location',
           'Problems.p_text': 'Problem Description ',
             'Problems.p_category':'Category' }
    if request.vars.PID!=None:
        dp=request.vars.PID
        lst=cats.categorizeProb(dp)
        for i in lst:
            var=i
        #PsudoTables=db(db.Problems.p_category==var).select()
        if auth.user_id!=None:
            constraints={'Problems':((var==db.Problems.p_category)&(db.Problems.p_loc==locs.Loc))}
        else:
            constraints={'Problems':var==db.Problems.p_category}
    else:
        if auth.user_id!=None:
            constraints={'Problems':locs.Loc==db.Problems.p_loc}
        else:
            constraints={'Problems':db.Problems.p_id>0}
    form=SQLFORM.smartgrid(db.Problems,constraints=constraints,searchable=False,sortable=True,paginate=10,headers=headers,fields=fields,selectable=None,exportclasses=export_classes,maxtextlength =64,csv=False,links=links,user_signature=True)

    return locals()
def upload_prob():
    portal="portal"
    status="Pending"
    Prob=db.Problems(request.args(0))
    pp=ids.generate_pid(request)
    db.Problems.p_id.default=pp
    form=SQLFORM(db.Problems)
    #snd=local_import('sendMail')
    dp=form.vars.loc
    #db.Problems.posted_on.default=request.now
    if form.process().accepted: #onvalidation=checkMail
        response.flash='Thank You, Your Problem Has Been Successfully Submitted'
        #Classification Algorithm method here
        rnk.db=db
        catlist=cats.categorizeProb(form.vars.p_text)
        for i in catlist:
            #db(db.Problems.p_id==pp-1).update(p_category=i)
            db.Problems.insert(p_category=i,p_id=pp,p_loc=form.vars.p_loc,p_text=form.vars.p_text,problem_source=portal,p_userid=form.vars.p_userid)
            rnk.r_ank(form.vars.p_loc,i,portal)


        #MAIL SENT METHOD HERE

        #sendMailToCollege(pp)
        #redirect(URL(r=request,f='index'))
    elif form.errors:
        ids.destroy_pid(request)
        response.flash=form.errors
    else:
        ids.destroy_pid(request)
        response.flash='Upload Your Problem'
    return locals()
#def cat():
@auth.requires_login()
def index():
    if db.auth_user.email!=None:
        mail = db(db.auth_user.id == auth.user_id).select(db.auth_user.email).first()
        if mail.email=='knitishnitj@gmail.com' or mail.email=='setiadeepanshu@gmail.com':
            redirect(URL(r=request,f='browse_prob_admin'))
        else:
            redirect(URL(r=request,f='Browse_problem'))
    form=SQLFORM(db.Locate)
    return dict(form=form)
def relatedsolution():
    pp=db(request.args[0]==db.Problems.id).select()
    return locals()
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def abc():
    return dict(message='')

def superadmin():
    form1=SQLFORM(db.Colleges)
    if form1.process().accepted:
        response.flash='Thank You, New College Has Been Successfully Added'
        redirect(URL(r=request,f='superadmin'))
    elif form1.errors:
        response.flash='Please Check The Form Again'
    else:
        response.flash='Add New College Here'
    return dict(form1=form1)
@service.csv
@service.rss
@service.xml
def browse_prob_admin():
    export_classes = dict(csv=True, json=True, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    prob = SQLFORM.grid(db.Problems, showbuttontext=False,user_signature=False)
    return dict(prob=prob)

def browse_sol_admin():
    export_classes = dict(csv=True, json=True, html=False,
                          tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    sol = SQLFORM.grid(db.Solutions, showbuttontext=False,user_signature=False)
    return dict(sol=sol)

def superadmin1():
    return dict(form)

def About_us():
    return dict(message='A digital web tool for gathering local relevant problems by analysis of problems posted directly or on social networking sites (Hash Tag) and then categorizing them in various domains i.e., departments etc. Problems reported to nearby institutes and are taken by department heads. After approval by department heads solutions of problems assigned to faculty and student teams are submitted. Problem solvers can get engage with the problem givers. Courses recommended after analysis of archived data')

def Contact_us():
    return dict(message='I am working')

def collaboration():
    return locals()
def console():
    return locals()
# -*- coding: utf-8 -*-
# try something like
from slackclient import SlackClient
def join(uid):
    v=db(db.Slck.user_id==uid).select(db.Slck.slack_pass)
    sc = SlackClient(v)
    x = sc.api_call("channels.join",name="MyChannel")
    x=x["channel"]["id"]
    y = db(db.Col).select(db.Col.ch_id)
    if y==None:
        db.Col.insert(ch_id=x)
    
def postMessage():
    v=db(db.Slck.user_id==uid).select(db.Slck.slack_pass)
    sc = SlackClient(v)
    x=sc.api_call("chat.postMessage",name="MyChannel",text=request.vars.text)
    y=db(db.Col).select(db.Col.ch_id).first()
    x=sc.api_call("channels.history",channel=y.ch_id)
    db(db.Col.ch_id==y.ch_id).update(json_data=x)
