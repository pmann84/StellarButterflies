from .sqlite_query_builder import SqliteSelectBuilder

def get_observed_sunspots_in_date_range(fromDateStr, toDateStr):
    qryBuilder = SqliteSelectBuilder()
    queryString = qryBuilder.sSelect("observed_datetime", "latitude") \
                            .sFrom("sunspots") \
                            .sWhere("observed_datetime") \
                            .sGt(fromDateStr) \
                            .sAnd("observed_datetime") \
                            .sLt(toDateStr) \
                            .endWhere() \
                            .endSelect()
    return queryString

def get_sunspot_count_in_date_range(fromDateStr, toDateStr):
    qryBuilder = SqliteSelectBuilder()
    queryString = qryBuilder.sSelect("observed_datetime", "count(uuid)") \
                            .sFrom("sunspots") \
                            .sWhere("observed_datetime") \
                            .sGt(fromDateStr) \
                            .sAnd("observed_datetime") \
                            .sLt(toDateStr) \
                            .endWhere() \
                            .sGroupBy("observed_datetime") \
                            .endSelect()
    return queryString

#select observed_datetime, count(uuid) from sunspots where observed_datetime > "<FROM_DATE>" AND observed_datetime < "<TO_DATE>" group by observed_datetime