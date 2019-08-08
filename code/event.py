#file: event.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains the event class.

from __future__ import absolute_import

from code import g, effect
from code.spec import GenericSpec, SpecDataField, spec_field_effect


class EventSpec(GenericSpec):

    spec_data_fields = [
        SpecDataField('event_type', data_field_name='type'),
        spec_field_effect(mandatory=True),
        SpecDataField('chance', converter=int),
        SpecDataField('unique', converter=int, default_value=0),
        SpecDataField('duration', converter=int, default_value=0),
    ]

    def __init__(self, id, event_type, effect_data, chance, duration, unique):
        super(EventSpec, self).__init__(id)
        self.event_type = event_type
        self.effect = effect.Effect(self, effect_data)
        self.chance = chance
        self.duration = duration if duration > 0 else None
        self.unique = unique
        if duration < 1 and not unique:
            raise ValueError("Event %s must have either a non-zero duration (e.g. duration = 21) or be unique "
                             "(unique = 1)")


class Event(object):
    # For some as-yet-unknown reason, cPickle decides to call event.__init__()
    # when an event is loaded, but before filling it.  So Event pretends to
    # allow no arguments, even though that would cause Bad Things to happen.
    def __init__(self, spec=None):
        self.spec = spec
        self.description = ""
        self.log_description = ""
        self.triggered = 0
        self.triggered_at = -1

    @property
    def event_id(self):
        return self.spec.id

    @property
    def event_type(self):
        return self.spec.event_type

    @property
    def effect(self):
        return self.spec.effect

    @property
    def chance(self):
        return self.spec.chance

    @property
    def duration(self):
        return self.spec.duration

    @property
    def unique(self):
        return self.spec.unique

    @property
    def decayable_event(self):
        return self.duration is not None

    def new_day(self):
        if not self.decayable_event:
            return

        if g.pl.raw_sec - self.triggered_at > self.duration * g.seconds_per_day:
            print("Before: %s" % str(g.pl.groups['news'].__dict__))
            self.effect.undo_effect()
            print("After: %s" % str(g.pl.groups['news'].__dict__))
            self.triggered = 0
            self.triggered_at = -1

    def convert_from(self, old_version):
        if old_version < 99: # < 1.0dev
            self.log_description = ""
        if old_version < 99.2: # < 1.0dev
            self.id = self.name
            self.effect = effect.Effect(self, [self.result[0], self.result[1]])
            del self.result

    def trigger(self):
        g.map_screen.show_message(self.description)

        self.triggered = 1
        self.triggered_at = g.pl.raw_sec

        self.effect.trigger()
