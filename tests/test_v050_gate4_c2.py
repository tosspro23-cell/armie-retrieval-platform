import unittest
from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract, TemporalConstraint, TemporalOperator
from armie_retrieval.models import Query, ResultItem, RetrievalPlan, RetrievalResult
from armie_retrieval.retrievers.c2_postfilter import C2PostFilterRetriever

class DenseStub:
    def __init__(self, items): self.items=tuple(items); self.calls=[]
    def retrieve(self, query, plan):
        self.calls.append(plan.parameters.get('retrieval_candidate_k'))
        return RetrievalResult(items=self.items[:plan.top_k], plan_id=plan.plan_id, strategy='dense', latency_ms=1.0, provenance={'strategy_identity':'C0'}, trace=('dense',))

def item(i, years, industry='Energy', role='Engineer', rank=2):
    return ResultItem(id=i, object_type='expert', title=i, content=i, metadata={'years_experience':years, 'industries':[industry], 'roles':[role], 'locations':['Lisbon'], 'seniority':'senior', 'seniority_rank':rank}, score=1.0-float(ord(i[0])-65)/100)

class C2Tests(unittest.TestCase):
    def setUp(self): self.stub=DenseStub([item('A',8),item('B',21),item('C',None),item('D',27,'Banking')])
    def test_order_preservation_and_shortfall(self):
        c=RetrievalContract(semantic_query='x',hard_constraints=(Constraint(canonical_field='years_experience',operator=ConstraintOperator.GTE,expected_value=20,category=ConstraintCategory.NUMERIC),))
        out=C2PostFilterRetriever(self.stub,candidate_pool_size=10).retrieve(Query('x',top_k=5,retrieval_contract=c),RetrievalPlan(strategy='dense',top_k=5))
        self.assertEqual([x.id for x in out.items],['B','D']); self.assertEqual(out.provenance['strict_shortfall_count'],3); self.assertEqual(self.stub.calls,[10])
    def test_exclusion_and_conjunction(self):
        c=RetrievalContract(semantic_query='x',hard_constraints=(Constraint(canonical_field='role',operator=ConstraintOperator.EQ,expected_value='Engineer',category=ConstraintCategory.ROLE),),exclusions=(Constraint(canonical_field='industry',operator=ConstraintOperator.EQ,expected_value='Banking',category=ConstraintCategory.CATEGORICAL),))
        out=C2PostFilterRetriever(self.stub,candidate_pool_size=20).retrieve(Query('x',retrieval_contract=c),RetrievalPlan(strategy='dense',top_k=5)); self.assertEqual([x.id for x in out.items],['A','B','C'])
        self.assertEqual(out.provenance['strategy_identity'],'C2')
    def test_unknown_is_excluded_and_no_hidden_expansion(self):
        c=RetrievalContract(semantic_query='x',hard_constraints=(Constraint(canonical_field='years_experience',operator=ConstraintOperator.GTE,expected_value=20,category=ConstraintCategory.NUMERIC),))
        out=C2PostFilterRetriever(self.stub,candidate_pool_size=10).retrieve(Query('x',top_k=1,retrieval_contract=c),RetrievalPlan(strategy='dense',top_k=1)); self.assertNotIn('C',[x.id for x in out.items]); self.assertEqual(self.stub.calls,[10])
    def test_deferred_contract_is_explicit(self):
        c=RetrievalContract(semantic_query='x',temporal_constraints=(TemporalConstraint(operator=TemporalOperator.AFTER,start=__import__('datetime').date(2020,1,1)),))
        out=C2PostFilterRetriever(self.stub).retrieve(Query('x',retrieval_contract=c),RetrievalPlan(strategy='dense',top_k=5)); self.assertEqual(out.items,()); self.assertEqual(self.stub.calls,[])
    def test_pool_sizes_are_explicit(self):
        for n in (10,20,30,50,100): self.assertEqual(C2PostFilterRetriever(self.stub,candidate_pool_size=n).candidate_pool_size,n)
        with self.assertRaises(ValueError): C2PostFilterRetriever(self.stub,candidate_pool_size=15)

if __name__=='__main__': unittest.main()
