"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from tortoise import Tortoise, fields, run_async
from tortoise.expressions import Q
from tortoise.models import Model


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ReverseRelation["Event"]

    def __str__(self):
        return self.name

    class Meta:
        table = "Tournament"


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    tournament: fields.ForeignKeyRelation[Tournament] = fields.ForeignKeyField(
        "models.Tournament", related_name="events"
    )
    participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name

    class Meta:
        table = "Event"


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ManyToManyRelation[Event]

    def __str__(self):
        return self.name

    class Meta:
        table = "Team"


async def run():
    mysql_user = 'root'
    mysql_password = '123456'
    mysql_db = 'yk_local_test'
    mysql_host = '172.31.10.148'
    mysql_port = 13306
    await Tortoise.init(db_url=f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}",
                        modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    tournament = Tournament(name="Tournament")
    await tournament.save()

    second_tournament = Tournament(name="Tournament 2")
    await second_tournament.save()

    event_first = Event(name="1", tournament=tournament)
    await event_first.save()
    a1 = await Event.all().select_related("tournament")
    print("a1",a1[0].tournament.id)
    event_second = await Event.create(name="2", tournament=second_tournament)
    await Event.create(name="3", tournament=tournament)
    await Event.create(name="4", tournament=second_tournament)

    await Event.filter(tournament=tournament)

    team_first = Team(name="First")
    await team_first.save()
    team_second = Team(name="Second")
    await team_second.save()

    await team_first.events.add(event_first)
    await event_second.participants.add(team_second)
    # await event_second.participants.add(team_first.id)

    print("暗室逢灯",
          await Event.filter(Q(id__in=[event_first.id, event_second.id]) | Q(name="3"))
          .filter(participants__not=team_second.id)
          .order_by("tournament__id")
          .distinct()
          )

    from tortoise.query_utils import Prefetch
    tournament_with_filtered = (
        await Tournament.all()
        .prefetch_related(Prefetch("events", queryset=Event.filter(name="1")))
        .first()
    )

    print("join", tournament_with_filtered.events[0])
    prefe = await Tournament.all().prefetch_related(Prefetch("events", queryset=Event.filter(name="2"), to_attr="event_name"))
    # for i in prefe:
    #     print(i.events)
    #     for j in i.event_name:
    #         print(j.name)
    # print(prefe.event_name[0].name)
    # prefe.events.all().first().values_list("name


    tournament_with_filtered_to_attr = (
        await Tournament.all()
        .prefetch_related(
            Prefetch("events", queryset=Event.filter(name="1"), to_attr="to_attr_events_first"),
            Prefetch(
                "events", queryset=Event.filter(name="1"), to_attr="to_attr_events_second"
            ),
        )
        .first()
    )
    print(tournament_with_filtered_to_attr)
    print("to_attr_events_first",tournament_with_filtered_to_attr.to_attr_events_first)
    print("to_attr_events_second",tournament_with_filtered_to_attr.to_attr_events_second)


    print("噶尔冻干粉", await Team.filter(events__tournament_id=tournament.id).order_by("-events__name"))
    print("啊是的法规",
        await Tournament.filter(events__name__in=["1", "3"])
        .order_by("-events__participants__name")
        .distinct()
    )

    print("收到货", await Team.filter(name__icontains="CON"))

    print("Firs", await Tournament.filter(events__participants__name__startswith="Fir"))
    print("count", await Tournament.filter(id__icontains=1).count())

if __name__ == "__main__":
    run_async(run())
