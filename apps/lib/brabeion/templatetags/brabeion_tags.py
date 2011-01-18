from django import template

from brabeion.models import BadgeAward


register = template.Library()


class BadgeCountNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            return cls(bits[1])
        elif len(bits) == 4:
            if bits[2] != "as":
                raise template.TemplateSyntaxError("Second argument to %r must "
                    "be 'as'" % bits[0])
            return cls(bits[1], bits[3])
        raise template.TemplateSyntaxError("%r takes either 1 or 3 arguments." % bits[0])
    
    def __init__(self, badge_recipient, context_var=None):
        self.badge_recipient = template.Variable(badge_recipient)
        self.context_var = context_var
    
    def render(self, context):
        badge_recipient = self.badge_recipient.resolve(context)
        badge_count = BadgeAward.objects.filter(badge_recipient=badge_recipient).count()
        if self.context_var is not None:
            context[self.context_var] = badge_count
            return ""
        return unicode(badge_count)

@register.tag
def badge_count(parser, token):
    """
    Returns badge count for a badge_recipient, valid usage is::

        {% badge_count badge_recipient %}
    
    or
    
        {% badge_count badge_recipient as badges %}
    """
    return BadgeCountNode.handle_token(parser, token)


class BadgesForBadgeRecipientNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) != 4:
            raise template.TemplateSyntaxError("%r takes exactly 3 arguments." % bits[0])
        if bits[2] != "as":
            raise template.TemplateSyntaxError("The 2nd argument to %r should "
                "be 'as'" % bits[0])
        return cls(bits[1], bits[3])
    
    def __init__(self, badge_recipient, context_var):
        self.badge_recipient = template.Variable(badge_recipient)
        self.context_var = context_var
    
    def render(self, context):
        badge_recipient = self.badge_recipient.resolve(context)
        context[self.context_var] = BadgeAward.objects.filter(
            badge_recipient=badge_recipient
        ).order_by("-awarded_at")
        return ""
        

@register.tag
def badges_for_badge_recipient(parser, token):
    """
    Sets the badges for a given badge_recipient to a context var.  Usage:
        
        {% badges_for_badge_recipient badge_recipient as badges %}
    """
    return BadgesForBadgeRecipientNode.handle_token(parser, token)
