import static org.junit.Assert.*;
import org.junit.*; 

import java.util.*;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.cfg.Configuration;

import com.gtfsdb.db.*; 


public class GtfsdbHibernate
{
    @Before
    public void testSetup()
    {
          System.out.println("Test start.");
    } 

    @After
    public void testComplete()

    {
          System.out.println("Test complete.");
    } 

    @Test
    public void testUniversalCalendar()
    {
          try
          {
              System.out.println("S");
              List<UniversalCalendar> list = (List<UniversalCalendar>)HibernateUtil.getSession().createCriteria(UniversalCalendar.class).list();
              assertTrue("Universal Calendar: is empty.", list.size() > 0);
              
              for(UniversalCalendar l : list)
                  System.out.println(l.getId().getServiceId() + " = " + l.getId().getDate());
          }
          catch (AssertionError e)
          {
                System.out.println("ASSERTION ERROR: " + e.getMessage());
          }
          catch (Exception e)
          {
                System.out.println("EXCEPTION: " + e.getMessage());
          }
    } 
}
