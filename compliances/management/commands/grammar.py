#
# bnf.py - BNF definition for XREF definitions
#

from datetime import datetime, timedelta

from pyparsing import (
    autoname_elements,
    Literal,
    Word,
    oneOf,
    infixNotation,
    OneOrMore,
    ZeroOrMore,
    SkipTo,
    Forward,
    delimitedList,
    Group,
    ungroup,
    Optional,
    alphas,
    restOfLine,
    alphanums,
    Suppress,
    QuotedString,
    ParseResults,
    ParseException,
    Keyword,
    Regex,
    infixNotation, 
    opAssoc,
    ParserElement,
    pyparsing_common
)

bnf = None

def XREF_GRAMMAR():
    global bnf

    if not bnf:

        # define keywords and simple infix notation grammar for boolean
        # expressions
        TRUE = Keyword("True")
        FALSE = Keyword("False")
        NOT = Keyword("not")
        AND = Keyword("and")
        OR = Keyword("or")

        # punctuation
        (
            colon,
            lbrace,
            rbrace,
            lbrack,
            rbrack,
            lparen,
            rparen,
            equals,
            comma,
            dot,
            slash,
            bslash,
            star,
            semi,
            langle,
            rangle,
        ) = map(Literal, r":{}[]()=,./\*;<>")

        # keywords
        (
            domain_,
            section_,
            requirement_,
            every_,
            exists_,
            within_,
            classified_,
            organized_,
            attended_,
            with_,
            as_,
            there_,
            for_,
            organized_,
            year_,
            years_,
            month_,
            months_,
            week_,
            weeks_,
            which_,
            has_,
            been_,
        ) = map(
            Keyword,
            '''domain section requirement every exists within classified organized attended with as there for organized year years month months week weeks which has been'''.split(),
        )

        Workflow = Keyword("Workflow")
        Employee = Keyword("Employee")
        Team = Keyword("Team")
        Training = Keyword("Training")

        entityType = Workflow | Employee | Team | Training

        identifier = Word(alphas, alphanums + "_" + "-")

        qualifiedIdentifier = delimitedList(identifier, ".", combine=True)

        docString = QuotedString(quote_char='"""', multiline=True)

        operator = Regex(">=|<=|!=|>|<|=").setName("operator")
        comparison_term = identifier | pyparsing_common.number | QuotedString(quote_char='"')
        condition = Group(TRUE | FALSE | comparison_term + operator + comparison_term)

        expr = infixNotation(condition,[
                              ("not", 1, opAssoc.RIGHT, ),
                              ("and", 2, opAssoc.LEFT, ),
                              ("or", 2, opAssoc.LEFT, ),])

        assign = Literal(":=")

        classification = QuotedString(quote_char='"').set_results_name("classification")

        termDef = Group(
            identifier.set_results_name("name")
            + assign
            + entityType.set_results_name("entity_type")
            + Optional(classified_ + Optional(as_) + classification)
            + Optional(with_ + expr.set_results_name("with"))
            + semi)

        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i+n]

        def time_span_parse_action(x):
            d = datetime.now()
            for l, dur in chunks(x[0], 2):
                if dur.startswith("year"):
                    d -= timedelta(days=l * 365.2425)
                elif dur.startswith("month"):
                    d -= timedelta(days=l * 30)
                elif dur.startswith("day"):
                    d -= timedelta(days=l)
                else:
                    raise ValueError("Invalid duration: " + dur)
            return d.strftime("%Y-%m-%d")

        timeSpan = year_ | years_ | month_ | months_ | week_ | weeks_
        timeSpanDef = OneOrMore(
            pyparsing_common.integer + timeSpan
        )

        withinDef = Group(
            Suppress(within_) 
            + timeSpanDef
        ).add_parse_action(time_span_parse_action).set_results_name("within")

        attendedDef = Group(
            Suppress(Optional(has_))
            + Suppress(attended_)
            + identifier.set_results_name("name")
            + Optional(withinDef)
        ).set_results_name("attended")

        organizedDef = Group(
            Suppress(Optional(which_ + has_ + been_))
            + Suppress(organized_)
            + Optional(withinDef)
        ).set_results_name("organized")

        existsConstraint = Group(
            Suppress(Optional(there_))
            + Suppress(exists_)
            + identifier.set_results_name("name")
            + Optional(organizedDef)
        ).set_results_name("exists")

        everyConstraint = Group(
            Suppress(every_)
            + identifier.set_results_name("name")
            + Optional(attendedDef)
        ).set_results_name("every")

        typeName = (
            qualifiedIdentifier
        ).set_results_name("type")

        qualifierName = Word(alphas, alphanums + '-' + '_').set_results_name("name")
        qualifierValue = (QuotedString(quote_char='"') | Word(alphanums + '-' + '_')).set_results_name("value")
        qualifierDef = Group(qualifierName + Optional(colon + qualifierValue))
        qualifiersDef = delimitedList(qualifierDef, ",").set_results_name("qualifiers")

        typeDef = (typeName + Optional(lbrack + qualifiersDef + rbrack))

        constraintTerm = existsConstraint | everyConstraint

        constraintDef = Group(
            Optional(docString).set_results_name("doc")
            + identifier.set_results_name("slug") + colon
            + constraintTerm
            + Suppress(semi)
        )

        requirementDef = Group(
            Optional(docString).set_results_name("doc")
            + requirement_
            + identifier.set_results_name("slug")
            + Optional(lbrack + qualifiersDef + rbrack)
            + lbrace
            + ZeroOrMore(constraintDef).set_results_name("constraints")
            + rbrace
        )

        sectionDef = Group(
            Optional(docString).set_results_name("doc")
            + section_
            + identifier.set_results_name("slug")
            + Optional(lbrack + qualifiersDef + rbrack)
            + lbrace
            + ZeroOrMore(requirementDef).set_results_name("requirements")
            + rbrace
        )

        domainDef = Group(
            Optional(docString).set_results_name("doc")
            + domain_
            + identifier.set_results_name("slug")
            + Optional(lbrack + qualifiersDef + rbrack)
            + lbrace
            + ZeroOrMore(termDef).set_results_name("terms")
            + ZeroOrMore(sectionDef).set_results_name("sections")
            + rbrace
        ).set_results_name("domain")

        bnf = domainDef

        autoname_elements()
        singleLineComment = "#" + restOfLine
        bnf.ignore(singleLineComment)

    return bnf

if __name__ == "__main__":

    import pprint

    def test(strng):
        global testnum
        print(strng)
        try:
            bnf = XREF_GRAMMAR()
            tokens = bnf.parse_string(strng)
            print("tokens = ")
            pprint.pprint(tokens.as_dict())
        except ParseException as err:
            print(err.line)
            print(" " * (err.column - 1) + "^")
            print(err)
        print()

    test(
        '''
        domain ISO27001 {
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            section Foo {
            }
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            SecurityWorkflow := Workflow classified as "security-incident" with False and not True or True and False;
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            SecurityWorkflow := Workflow classified as "security-incident" with a="a" and b=2;
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            SecurityWorkflow := Workflow classified as "security-incident" with a="a" and b=2;

            section A [name:"Processes"] {
                requirement A1 {
                    wf1: exists SecurityWorkflow;
                }
            }
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            SecurityWorkflow := Workflow classified as "security-incident" with a="a" and b=2;
            section A [name:"Personnel"] {
                requirement A1 {
                    wf1: every SecurityWorkflow;
                }
            }
        }
        '''
    )
    test(
        '''
        """
        Doc
        """
        domain ISO27001 {
            """
            Doc
            """
            section A [name:"Personnel"] {
                """
                Doc
                """
                requirement A1 {
                    """
                    Doc
                    """
                    wf1: every SecurityWorkflow;
                }
            }
        }
        '''
    )
    test(
        '''
        domain ISO27001 {
            BasicSecurityTraining := Training classified as "basic-security-training";
            SecurityWorkflow := Workflow classified as "security-incident" with type="incident" and status="published";
            section A [name:"Personnel"] {
                requirement A1 {
                    wf1: every SecurityEmployee has attended BasicSecurityTraing within 2 years 3 months;
                }
                requirement A2 {
                    wf2: there exists BasicSecurityTraining which has been organized within 2 years;
                }
            }
        }
        '''
    )

    test(
        '''
        domain iso27001 {
            SecurityIncidentWorkflow := Workflow classified as "security-incident" with status="published" and type="incident";

            SecurityEmployee := Employee classified as "security-employee";

            BasicSecurityTraining := Training classified as "basic-security-training";

            section A [name:"Processes"] {
                requirement A1 {
                    wf-exists: there exists SecurityIncidentWorkflow;
                }

            }
        }
        '''
    )
