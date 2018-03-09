class SqliteSelectBuilder:
    def __init__(self):
        self.query_str = ""
        self.columns = []
        self.table_name = ""
        self.where_clause = ""
        self.group_by = []

    def sSelect(self, *columns):
        for col in columns:
            self.columns.append(col)
        return self

    def sFrom(self, table_name):
        self.table_name = table_name
        return self

    def sWhere(self, column_name):
        where_clause_builder = SqliteWhereBuilder(self, column_name)
        return where_clause_builder

    def sGroupBy(self, column_name):
        self.group_by.append(column_name)
        return self
        
    def endSelect(self):
        # Setup SELECT
        if len(self.columns) == 0:
            raise "Must call select!"
        self.query_str = "SELECT "
        self.query_str += ", ".join(self.columns)
        # Setup FROM
        self.query_str += " FROM "
        if self.table_name == "":
            raise "Must call from!"
        self.query_str += self.table_name
        # SETUP WHERE 
        if self.where_clause != "":
            self.query_str += " WHERE "
            self.query_str += self.where_clause
        # GROUP BY
        if len(self.group_by) > 0:
            self.query_str += " GROUP BY "
            self.query_str += ", ".join(self.group_by)
        return self.query_str

class SqliteWhereBuilder:
    def __init__(self, parent_query, column_name):
        self.parent_query = parent_query
        self.column_name = column_name
        self.where_clause_expression = self.column_name
        # states
        self.started_where = True

    def sEq(self, str_value):
        self.__rhs_where("=", str_value)
        return self

    def sGt(self, str_value):
        self.__rhs_where(">", str_value)
        return self

    def sLt(self, str_value):
        self.__rhs_where("<", str_value)
        return self

    def __rhs_where(self, str_operator, str_value):
        if not self.started_where:
            raise "Cannot define rhs of an expression without starting a where clause"
        self.where_clause_expression += " "
        self.where_clause_expression += str_operator
        self.where_clause_expression += " \""
        self.where_clause_expression += str_value
        self.where_clause_expression += "\""
        self.started_where = False
        return self

    def sAnd(self, column_name):
        if self.started_where:
            raise "Can't start new where clause in the middle of another!"
        self.started_where = True
        self.where_clause_expression += " AND "
        self.where_clause_expression += column_name
        return self

    def endWhere(self):
        self.parent_query.where_clause = self.where_clause_expression
        return self.parent_query