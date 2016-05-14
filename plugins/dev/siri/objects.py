from copy import copy
import uuid


class SiriMetaClass(type):
    def __new__(cls, name, bases, attrs):
        parent_props = []
        for base in bases:
            if hasattr(base, '_properties'):
                parent_props += base._properties
        cls_props = []
        for attr in filter(lambda a: (not a.startswith('_')) or callable(a), attrs.iterkeys()):
            if not attr in parent_props:
                cls_props.append(attr)
        attrs['_properties'] = cls_props
        return super(SiriMetaClass, cls).__new__(cls, name, bases, attrs)


class SiriObject(object):
    __metaclass__ = SiriMetaClass
    cls = ""
    group = "com.apple.ace.assistant"

    def __init__(self, **kwargs):
        self.ref_id = kwargs.get('ref_id', None)
        self.ace_id = kwargs.get('ace_id', None)
        for key in self._properties:
            val = kwargs.get(key, copy(getattr(self.__class__, key)))
            setattr(self, key, val)

    def to_dict(self):
        d = {
            'class': self.cls,
            'group': self.group,
            'properties': {}
        }
        if self.ref_id:
            d['refId'] = self.ref_id
        if self.ace_id:
            d['aceId'] = self.ace_id
        props = d['properties']
        for key in self._properties:
            val = getattr(self, key)
            if isinstance(val, list):
                props[key] = []
                for el in val:
                    if hasattr(el, 'to_dict'):
                        props[key].append(el.to_dict())
                    else:
                        props[key].append(el)
            else:
                if hasattr(val, 'to_dict'):
                    props[key] = val.to_dict()
                else:
                    props[key] = val
        return d

    def make_root(self, ref_id=None, ace_id=None):
        if not ref_id:
            ref_id = str(uuid.uuid4()).upper()
        if not ace_id:
            ace_id = str(uuid.uuid4())
        self.ref_id = ref_id
        self.ace_id = ace_id


class SiriObjects(object):
    class AddViews(SiriObject):
        """
            A command received by the iPhone informing it to draw something

            Properties:
                `scrollToTop`
                    Scroll to new views the top of the screen (I presume?)
                `temporary`
                    Doesn't act like I'd expect, not so sure of this one
                `dialogPhase`
                    Doesn't seem to matter too much, but varies
                `views`
                    A list of either `Utterance`, or `Wolfram` instances
        """
        cls = "AddViews"
        scrollToTop = False
        temporary = False
        dialogPhase = "Completion"
        views = []

    class Utterance(SiriObject):
        """
            The "Meat & Potatoes" of the SiriObjects, an Utterance prompts a
            textual and (optionally) a voice prompt.

            Properties:
                `text`
                    Text to display on screen.
                `speakableText`
                    Text to read, this will default to `text` if not provided.
                    This field also supports various @tts{} commands.
                `dialogIdentifier`
                    I'm not convinced these do a whole lot, they seem to vary
                    from things like Misc#ident (default) to
                    Answer#someSpecificQuestion and not much else changes.
                `listenAfterSpeaking`
                    Somewhat self-explainatory, defaults to False.
        """
        cls = "AssistantUtteranceView"
        text = ""
        speakableText = None
        dialogIdentifier = "Misc#ident"
        listenAfterSpeaking = False

        def __init__(self, *args, **kwargs):
            super(SiriObjects.Utterance, self).__init__(*args, **kwargs)
            if self.speakableText is None:
                self.speakableText = self.text

    class Wolfram(SiriObject):
        """
            The Wolfram Snippet, not surprisingly, shows Wolfram Results.
            This SiriObject is also the best way to insert images.

            Properties:
                `answers`
                    A list of `SiriObjects.Answer` instances
        """
        cls = "Snippet"
        group = "com.apple.ace.answer"
        answers = []

    class Answer(SiriObject):
        """
            The Answer Object provides the "sections" of a Wolfram Answer

            Properties:
                `title`
                    The title displayed on the purple background
                `lines`
                    A list of `SiriObject.AnswerLine` instances
        """
        cls = "Object"
        group = "com.apple.ace.answer"
        title = ""
        lines = []

    class AnswerLine(SiriObject):
        """
            The AnswerLine Object provides the content of a SiriObjects.Answer

            Properties:
                `text`
                    Text to display
                `image`
                    URL of a image to display
        """
        cls = "ObjectLine"
        group = "com.apple.ace.answer"
        text = ""
        image = ""

    class RequestCompleted(SiriObject):
        """ Send at the end of a request, self-explainatory. """
        cls = "RequestCompleted"
        group = "com.apple.ace.system"
