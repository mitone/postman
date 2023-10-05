import asyncpg


class DBStorage:
    pool: asyncpg.Pool

    async def init(self, dsn):
        print(dsn)
        self.__class__.pool = await asyncpg.create_pool(dsn)

    async def get_conn(self):
        return self.__class__.pool.acquire()

    async def release(self, conn):
        await self.__class__.pool.release(conn)

    async def fetch(self, query, *args, **kwargs) -> list:
        return await self.__class__.pool.fetch(query, *args, **kwargs)

    async def fetchrow(self, query, *args, **kwargs) -> list:
        return await self.__class__.pool.fetchrow(query, *args, **kwargs)

    async def execute(self, query: str, *args, **kwargs):
        return await self.__class__.pool.execute(query, *args, **kwargs)

    async def search_city(self, city_text):
        sql = """
            select id, country || ' / ' || name
            from geonames
            where lower(name) = lower($1)
            limit 11;
        """
        rows = await self.fetch(sql, city_text)

        if len(rows) == 0:
            sql = """
                select id, country || ' / ' || name
                from geonames
                where altnames ilike '%'|| $1 ||'%'
                limit 11;
            """
            rows = await self.fetch(sql, city_text)

        return rows

    async def new_travel(
        self,
        city_src: int,
        city_dst: int,
        travel_date,
        parcel_type: str,
        payment_type: str,
        user_id,
        user_username,
    ):
        sql = """
            insert into travels (city_src, city_dst, travel_date, parcel_type,
                                 payment_type, user_id, user_username)
            values ($1, $2, $3, $4, $5, $6, $7);
        """
        await self.execute(
            sql,
            city_src,
            city_dst,
            travel_date,
            parcel_type,
            payment_type,
            user_id,
            user_username,
        )


    async def get_user_travels(self, user_id: int):
        sql = """
        select t.id, g1.name as from, g2.name as to, travel_date
        from travels t
        join geonames g1 on t.city_src = g1.id
        join geonames g2 on t.city_dst = g2.id
        where t.user_id = $1 and active
        order by travel_date
        """

        rows = await self.fetch(sql, user_id)
        return rows

    # get travels until the date (including)
    async def get_travels(self, dt):
        sql = """
        select t.id, t.user_id
        from travels t
        where active and travel_date <= $1
        """

        rows = await self.fetch(sql, dt)
        return rows

    async def get_user_travels_count(self, user_id: int) -> int:
        ''' Get user travels count '''

        ''' To sort by date add filter: and travel_date >= current_date '''


        sql = """
        select count(*)
        from travels t
        where t.user_id = $1 and active
        """

        rows = await self.fetchrow(sql, user_id)
        return rows[0]

    async def get_travel(self, travel_id: int, user_id: int):
        sql = """
        select t.id, g1.name as from, g2.name as to, travel_date,
            parcel_type, payment_type, user_id, user_username
        from travels t
        join geonames g1 on t.city_src = g1.id
        join geonames g2 on t.city_dst = g2.id
        where t.id = $1 and t.user_id = $2
        """

        row = await self.fetchrow(sql, travel_id, user_id)
        return row

    # we always also use user_id in queries so the users can modify only their records
    # and we don't accidentally change or remove other user's data
    async def delete_travel(self, travel_id: int, user_id: int):
        sql = """
        delete from travels t
        where t.id = $1 and t.user_id = $2
        """

        await self.execute(sql, travel_id, user_id)

    async def change_travel(self, travel_id: int, user_id: int, field: str, val):
        sql = f"""
        update travels t
        set {field} = $3, updated = current_timestamp
        where t.id = $1 and t.user_id = $2
        """

        await self.execute(sql, travel_id, user_id, val)

    async def change_parcel(self, parcel_id: int, user_id: int, field: str, val):
        sql = f"""
        update parcels t
        set {field} = $3, updated = current_timestamp
        where t.id = $1 and t.user_id = $2
        """

        await self.execute(sql, parcel_id, user_id, val)

    async def mark_parcel_notified(self, parcel_id: int, user_id: int):
        sql = f"""
        update parcels t
        set updated = current_timestamp, notified = true
        where t.id = $1 and t.user_id = $2
        """

        await self.execute(sql, parcel_id, user_id)

    async def change_travel_city_src(self, travel_id: int, user_id: int, city_id: int):
        await self.change_travel(travel_id, user_id, "city_src", city_id)

    async def change_travel_city_dest(self, travel_id: int, user_id: int, city_id: int):
        await self.change_travel(travel_id, user_id, "city_dst", city_id)

    async def get_user_parcels_count(self, user_id: int) -> int:
        sql = """
        select count(*)
        from parcels t
        where t.user_id = $1 and active and date_end >= current_date
        """

        rows = await self.fetchrow(sql, user_id)
        return rows[0]

    async def new_parcel(
        self,
        city_src: int,
        city_dst: int,
        date_end,
        parcel_type: str,
        user_id,
        user_username,
    ) -> int:
        sql = """
            insert into parcels (city_src, city_dst, date_end,
                parcel_type, user_id, user_username)
            values ($1, $2, $3, $4, $5, $6)
            returning id
        """
        row = await self.fetchrow(
            sql,
            city_src,
            city_dst,
            date_end,
            parcel_type,
            user_id,
            user_username,
        )
        return row[0]

    async def get_parcel(self, parcel_id: int, user_id: int):
        sql = """
        select p.id,
            g1.name as from,
            g2.name as to, date_end,
            parcel_type,
            user_id,
            user_username,
            search_by_countries
        from parcels p
        join geonames g1 on p.city_src = g1.id
        join geonames g2 on p.city_dst = g2.id
        where p.id = $1 and p.user_id = $2
        """

        row = await self.fetchrow(sql, parcel_id, user_id)
        return row

    async def get_user_parcels(self, user_id: int):
        sql = """
        select t.id, g1.name as from, g2.name as to, date_end
        from parcels t
        join geonames g1 on t.city_src = g1.id
        join geonames g2 on t.city_dst = g2.id
        where t.user_id = $1 and active
        order by date_end
        """

        rows = await self.fetch(sql, user_id)
        return rows

    async def delete_parcel(self, parcel_id: int, user_id: int):
        sql = """
        delete from parcels t
        where t.id = $1 and t.user_id = $2
        """

        await self.execute(sql, parcel_id, user_id)  


    async def search_travels_by_parcel(self, parcel_id: int):
        ''' We have a parcel and we want to find all travels matching that parcel '''

        '''
            Changes: 01.09.2023: added "or (t.travel_date IS NULL)" condition
        '''

        sql = """
        select distinct t.id, t.travel_date, t.payment_type, t.user_username, t.parcel_type
        from travels t
        join parcels p
            on p.id = $1
                and t.city_src = p.city_src and t.city_dst = p.city_dst
                and (t.parcel_type && p.parcel_type)
                and t.active and p.active
                and ((t.travel_date <= p.date_end
                and t.travel_date >= current_date
                and p.date_end >= current_date)
                or (t.travel_date IS NULL))
        order by t.travel_date desc NULLS first
        limit 10;
        """

        rows = await self.fetch(sql, parcel_id)
        return rows

    async def search_travels_by_parcel_on_countries(self, parcel_id: int):
        ''' We have a parcel and we want to find all travels matching that parcel
            but on countries level.

            Changes: 01.09.2023: added "or (t.travel_date IS NULL)" condition
        '''
        sql = """
        with countries as (
            select g1.country as country_src, g2.country as country_dst
            from parcels p
            join geonames g1 on g1.id = p.city_src
            join geonames g2 on g2.id = p.city_dst
            where p.id = $1
        )
        select t.id, g1.name as travel_from, g2.name as travel_to, t.travel_date, t.payment_type, t.user_username, t.parcel_type from travels t
        join geonames g1 on g1.id = t.city_src and g1.country = (select country_src from countries)
        join geonames g2 on g2.id = t.city_dst and g2.country = (select country_dst from countries)
        join parcels p on p.id = $1
        where (t.parcel_type && p.parcel_type)
            and t.active and p.active
            and ((t.travel_date <= p.date_end
            and t.travel_date >= current_date
            and p.date_end >= current_date)
            or (t.travel_date IS NULL))
        order by p.id, t.travel_date
        """

        rows = await self.fetch(sql, parcel_id)
        return rows

    async def search_travels_for_all_with_exact_cities(self):
        sql = """
        select distinct p.id, p.user_id, p.date_end,
            g1.name as from, g2.name as to,
            t.travel_date, t.payment_type, t.user_username,
            t.id as travel_id
        from travels t
        join parcels p
            on t.city_src = p.city_src and t.city_dst = p.city_dst
                and t.travel_date <= p.date_end
                and ((t.travel_date >= current_date
                and p.date_end >= current_date)
                or (t.travel_date IS NULL))
                and (t.parcel_type && p.parcel_type)
                and t.active and p.active
                and not p.search_by_countries
        join geonames g1 on p.city_src = g1.id
        join geonames g2 on p.city_dst = g2.id
        where not exists (select * from travel_suggestions s
                            where s.parcel_id = p.id and s.travel_id = t.id)
        order by p.id, t.travel_date
        """

        rows = await self.fetch(sql)
        return rows

    async def search_travels_for_all_by_countries(self):
        sql = """
        with parcels_c as (
            select g1.country as country_src, g2.country as country_dst, p.id,
                p.user_id, p.date_end, g1.name as from, g2.name as to, p.parcel_type
            from parcels p
            join geonames g1 on g1.id = p.city_src
            join geonames g2 on g2.id = p.city_dst
            where p.active and p.search_by_countries and ((p.date_end >= current_date) or (p.date_end is NULL))
        ),
        travels_c as (
            select g1.country as country_src, g2.country as country_dst,
                t.travel_date, t.payment_type, t.user_username,
                t.id, t.parcel_type,
                g1.name as from, g2.name as to
            from travels t
            join geonames g1 on t.city_src = g1.id
            join geonames g2 on t.city_dst = g2.id
            where t.active and ((t.travel_date >= current_date) or (t.travel_date is NULL))

        )
        select
            p.id, p.user_id, p.date_end,
            p.from, p.to,
            t.travel_date, t.payment_type, t.user_username,
            t.id as travel_id,
            t.from as travel_from,
            t.to as travel_to
        from parcels_c p
        join travels_c t on
                ((t.travel_date <= p.date_end) or (t.travel_date is NULL))
                and (t.parcel_type && p.parcel_type)
                and t.country_src = p.country_src
                and t.country_dst = p.country_dst
        where not exists (select * from travel_suggestions s
                            where s.parcel_id = p.id and s.travel_id = t.id)
        order by p.id, t.travel_date
        """

        rows = await self.fetch(sql)
        return rows

    async def add_suggestion(self, parcel_id, travel_id):
        sql = """
        insert into travel_suggestions values ($1, $2) on conflict do nothing;
        """
        await self.execute(sql, parcel_id, travel_id)

    # get parcels until the date (including), for which travels were suggested
    async def get_parcels(self, dt):
        sql = """
        select distinct p.id, g1.name as from, g2.name as to, date_end, user_id
        from parcels p
        join geonames g1 on p.city_src = g1.id
        join geonames g2 on p.city_dst = g2.id
        join travel_suggestions t on p.id = t.parcel_id
        where p.active and not p.notified and t.created <= $1 and p.updated <= $1
        order by date_end
        """

        rows = await self.fetch(sql, dt)
        return rows

    async def set_parcels_unactive(self):
        sql = """
        update parcels
        set active = false, updated = current_timestamp
        where date_end < (current_date - interval '1 day');
        """
        await self.execute(sql)

    async def add_event(self, user_id, username, event_name):
        sql = """
        insert into events (user_id, username, event) values ($1, $2, $3);
        """
        await self.execute(sql, user_id, username, event_name)

    async def get_contacts_by_parcels(self):
        sql = """
        select distinct user_id from parcels
        """
        rows = await self.fetch(sql)
        return rows
