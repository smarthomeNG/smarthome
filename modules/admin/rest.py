#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  Based on code by Anders Pearson
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import json
import cherrypy
import logging
import jwt


# """
# REST Resource
#
# cherrypy controller mixin to make it easy to build REST applications.
#
# handles nested resources and method-based dispatching.
#
# here's a rough sample of what a controller would look like using this:
#
# cherrypy.root = MainController()
# cherrypy.root.user = UserController()
#
# class PostController(RESTResource):
#     def index(self,post):
#         return post.as_html()
#     index.expose_resource = True
#
#     def delete(self,post):
#         post.destroySelf()
#         return "ok"
#     delete.expose_resource = True
#
#     def update(self,post,title="",body=""):
#         post.title = title
#         post.body = body
#         return "ok"
#     update.expose_resource = True
#
#     def add(self, post, title="", body="")
#         post.title = title
#         post.body = body
#         return "ok"
#     update.expose_resource = True
#
#     def REST_instantiate(self, slug):
#         try:
#             return Post.select(Post.q.slug == slug, Post.q.userID = self.parent.id)[0]
#         except:
#             return None
#
#     def REST_create(self, slug):
#         return Post(slug=slug,user=self.parent)
#
# class UserController(RESTResource):
#     REST_children = {'posts' : PostController()}
#
#     def index(self,user):
#         return user.as_html()
#     index.expose_resource = True
#
#     def delete(self,user):
#         user.destroySelf()
#         return "ok"
#     delete.expose_resource = True
#
#     def update(self,user,fullname="",email=""):
#         user.fullname = fullname
#         user.email = email
#         return "ok"
#     update.expose_resource = True
#
#     def add(self, user, fullname="", email=""):
#         user.fullname = fullname
#         user.email = email
#         return "ok"
#     add.expose_resource = True
#
#     def extra_action(self,user):
#         # do something else
#     extra_action.expose_resource = True
#
#     def REST_instantiate(self, username):
#         try:
#             return User.byUsername(username)
#         except:
#             return None
#
#     def REST_create(self, username):
#         return User(username=username)
#
# then, the site would have urls like:
#
#     /user/bob
#     /user/bob/posts/my-first-post
#     /user/bob/posts/my-second-post
#
# which represent REST resources. calling 'GET /usr/bob' would call the index() method on UserController
# for the user bob. 'PUT /usr/joe' would create a new user with username 'joe'. 'DELETE /usr/joe'
# would delete that user. 'GET /usr/bob/posts/my-first-post' would call index() on the Post Controller
# with the post with the slug 'my-first-post' that is owned by bob.
#
#
# """


class RESTResource:
    """
    REST Resource

    cherrypy controller mixin to make it easy to build REST applications.

    handles nested resources and method-based dispatching.

    here's a rough sample of what a controller would look like using this:

    cherrypy.root = MainController()
    cherrypy.root.user = UserController()

    class PostController(RESTResource):
        def index(self,post):
            return post.as_html()

        index.expose_resource = True

        def delete(self,post):
            post.destroySelf()
            return "ok"

        delete.expose_resource = True

        def update(self,post,title="",body=""):
            post.title = title
            post.body = body
            return "ok"

        update.expose_resource = True

        def add(self, post, title="", body="")
            post.title = title
            post.body = body
            return "ok"

        update.expose_resource = True

        def REST_instantiate(self, slug):
            try:
                return Post.select(Post.q.slug == slug, Post.q.userID = self.parent.id)[0]
            except:
                return None

        def REST_create(self, slug):
            return Post(slug=slug,user=self.parent)

    class UserController(RESTResource):
        REST_children = {'posts' : PostController()}

        def index(self,user):
            return user.as_html()

        index.expose_resource = True

        def delete(self,user):
            user.destroySelf()
            return "ok"

        delete.expose_resource = True

        def update(self,user,fullname="",email=""):
            user.fullname = fullname
            user.email = email
            return "ok"

        update.expose_resource = True

        def add(self, user, fullname="", email=""):
            user.fullname = fullname
            user.email = email
            return "ok"

        add.expose_resource = True

        def extra_action(self,user):
            # do something else

        extra_action.expose_resource = True

        def REST_instantiate(self, username):
            try:
                return User.byUsername(username)
            except:
                return None

        def REST_create(self, username):
            return User(username=username)

    then, the site would have urls like:

        /user/bob
        /user/bob/posts/my-first-post
        /user/bob/posts/my-second-post

    which represent REST resources. calling 'GET /usr/bob' would call the index() method on UserController
    for the user bob. 'PUT /usr/joe' would create a new user with username 'joe'. 'DELETE /usr/joe'
    would delete that user. 'GET /usr/bob/posts/my-first-post' would call index() on the Post Controller
    with the post with the slug 'my-first-post' that is owned by bob.

    """
    REST_dispatch_execute_warnlevel = 'WARNING'

    # default method mapping. ie, if a GET request is made for
    # the resource's url, it will try to call an index() method (if it exists);
    # if a PUT request is made, it will try to call an update() method.
    # if you prefer other method names, just override these values in your
    # controller with REST_map
    REST_defaults = {'DELETE' : 'delete',
                     'GET' : 'read',
                     'POST' : 'add',
                     'PUT' : 'update'}
    REST_map = {}

    # if the resource has children resources, list them here. format is
    # a dictionary of name -> resource mappings. ie,
    #
    # REST_children = {'posts' : PostController()}
    REST_children = {}

    logger = logging.getLogger('REST')
    jwt_secret = 'SmartHomeNG$0815'

    @cherrypy.expose
    def index(self, *vpath, **params):
        # self.logger.info("RESTResource.index {}".format(self.__class__.__name__))
        return self.default(*vpath, **params)


    def index2(self):
        self.logger.info("RESTResource index2 (nicht überschrieben){}".format(self.__class__.__name__))
        # Methode muss überschrieben werden
        return


    def REST_get_jwt_token(self):
        """
        get the (decoded) token that was used to make the request

        :return: tuple
        """
        # self.logger.debug("REST_get_jwt_token(): cherrypy.request.headers = {}".format(cherrypy.request.headers))
        token = cherrypy.request.headers.get('Authorization', '')
        decoded = {}
        # self.logger.debug("REST_test_jwt_token(): raw token = {}".format(token))
        if token != '':
            if token.startswith('Bearer '):
                token = token[len('Bearer '):]

        # self.logger.debug("REST_test_jwt_token(): jwt token = {}".format(token))
        if self.jwt_secret and (len(token) > 0):
            try:
                decoded = jwt.decode(token, self.jwt_secret, verify=True, algorithms='HS256')
            except Exception as e:
                self.logger.debug("REST_test_jwt_token(): Exception = {}".format(e))
                se = format(e)
                if se.endswith('expired'):
                    error_text = format(e)
                token = ''
                decoded = {}
        self.logger.debug("REST_test_jwt_token(): decoded jwt token = {}".format(decoded))

        if len(token) == 0:
            decoded = {}
        return decoded


    def REST_test_jwt_token(self):
        """
        test existance of jwt

        :return: tuple
        """
        error_text = 'Unauthorized'
        # self.logger.debug("REST_test_jwt_token(): cherrypy.request.headers = {}".format(cherrypy.request.headers))
        # token = cherrypy.request.headers.get('Authorization', '')
        # decoded = {}
        # # self.logger.debug("REST_test_jwt_token(): raw token = {}".format(token))
        # if token != '':
        #     if token.startswith('Bearer '):
        #         token = token[len('Bearer '):]
        #
        # # self.logger.debug("REST_test_jwt_token(): jwt token = {}".format(token))
        # if self.jwt_secret and (len(token) > 0):
        #     try:
        #         decoded = jwt.decode(token, self.jwt_secret, verify=True, algorithms='HS256')
        #     except Exception as e:
        #         self.logger.debug("REST_test_jwt_token(): Exception = {}".format(e))
        #         se = format(e)
        #         if se.endswith('expired'):
        #             error_text = format(e)
        #         token = ''
        #         decoded = {}
        # self.logger.debug("REST_test_jwt_token(): decoded jwt token = {}".format(decoded))
        decoded = self.REST_get_jwt_token()

        if decoded == {}:
            return (False, error_text)

        return (True, '')

    def REST_dispatch_execute(self, m, method, root, resource, **params):
        if m and getattr(m, "expose_resource", False):
            public_root = False
            if root:
                public_root = getattr(m, "public_root", False)
                self.logger.info("REST_dispatch_execute(): public_root = '{}'".format(public_root))
            if not public_root:
                auth_needed = getattr(m, "authentication_needed", False)
                self.logger.debug("REST_dispatch_execute(): {}Authentication needed for {} ({})".format(('' if auth_needed else 'No '), method, str(m).split()[2]))
                if auth_needed:
                    # self.logger.info("REST_dispatch: Authentication needed for {} ({})".format(method, str(m).split()[2]))
                    token_valid, error_text = self.REST_test_jwt_token()
                    if not token_valid:
                        self.logger.info("REST_dispatch_execute(): Authentication failed for {} ({})".format(method, str(m).split()[2]))
                        response = {'result': 'error', 'description': error_text}
                        return json.dumps(response)

            try:
                return m(resource, **params)
            except Exception as e:
                if self.module.rest_dispatch_force_exception:
                    self.logger.notice("The following exception is thrown, due to the configuration in etc/module.yaml:")
                    self.logger.exception(f"REST_dispatch_execute: {resource}: {e.__class__.__name__} {e}")
                else:
                    self.logger.warning(f"REST_dispatch_execute: {resource}: {e.__class__.__name__} {e}")
                response = {'result': 'error', 'description': f"{e.__class__.__name__} {e}"}
                return json.dumps(response)
        return None

    def REST_dispatch(self, root, resource, **params):
        # if this gets called, we assume that default has already
        # traversed down the tree to the right location and this is
        # being called for a raw resource
        method = cherrypy.request.method
        if method in self.REST_map:
            try:
                m = getattr(self,self.REST_map[method])
            except:
                self.logger.info("REST_dispatch *1: Unsupported method  = {} for resource '{}'".format(method, resource))
                raise cherrypy.HTTPError(status=404)
            result = self.REST_dispatch_execute(m, method, root, resource, **params)
            if result != None:
                return result
            else:
                raise cherrypy.NotFound
        else:
            if method in self.REST_defaults:
                try:
                    m = getattr(self,self.REST_defaults[method])
                except:
                    self.logger.info("REST_dispatch: Unsupported method  = {} for resource '{}'".format(method, resource))
                    raise cherrypy.HTTPError(status=404)
                result = self.REST_dispatch_execute(m, method, root, resource, **params)
                if result != None:
                    return result
                else:
                    raise cherrypy.NotFound

        raise cherrypy.NotFound

    @cherrypy.expose
    def default(self, *vpath, **params):
        if not vpath:
            resource = None
            # self.logger.info("RESTResource.default: vpath = '{}',  params = '{}'".format(list(vpath), dict(**params)))

            return self.REST_dispatch(True, resource, **params)
            # return list(**params)
        # self.logger.info("RESTResource.default: vpath = '{}',  params = '{}'".format(list(vpath), dict(**params)))
        # Make a copy of vpath in a list
        vpath = list(vpath)
        atom = vpath.pop(0)

        # Coerce the ID to the correct db type
        resource = self.REST_instantiate(atom)
        if resource is None:
            if cherrypy.request.method == "PUT":
                # PUT is special since it can be used to create
                # a resource
                resource = self.REST_create(atom)
            else:
                raise cherrypy.NotFound

        # There may be further virtual path components.
        # Try to map them to methods in children or this class.
        if vpath:
            a = vpath.pop(0)
            if a in self.REST_children:
                c = self.REST_children[a]
                c.parent = resource
                return c.default(*vpath, **params)
            method = getattr(self, a, None)
            if method and getattr(method, "expose_resource"):
                return method(resource, *vpath, **params)
            else:
                # path component was specified but doesn't
                # map to anything exposed and callable
                raise cherrypy.NotFound

        # No further known vpath components. Call a default handler
        # based on the method
        return self.REST_dispatch(False, resource,**params)

    def REST_instantiate(self,id):
        """ instantiate a REST resource based on the id

        this method MUST be overridden in your class. it will be passed
        the id (from the url fragment) and should return a model object
        corresponding to the resource.

        if the object doesn't exist, it should return None rather than throwing
        an error. if this method returns None and it is a PUT request,
        REST_create() will be called so you can actually create the resource.
        """
        return id
        # raise cherrypy.NotFound

    def REST_create(self,id):
        """ create a REST resource with the specified id

        this method should be overridden in your class.
        this method will be called when a PUT request is made for a resource
        that doesn't already exist. you should create the resource in this method
        and return it.
        """
        return id
        # raise cherrypy.NotFound

