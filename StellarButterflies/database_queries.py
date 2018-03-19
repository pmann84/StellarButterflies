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

def get_observed_sunspots_in_date_range_coloured_by_area(fromDateStr, toDateStr):
    qryBuilder = SqliteSelectBuilder()
    queryString = qryBuilder.sSelect("observed_datetime", "latitude", "corr_whole_spot_area") \
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