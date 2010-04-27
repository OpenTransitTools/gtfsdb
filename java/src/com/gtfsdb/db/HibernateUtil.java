package com.gtfsdb.db;

import java.util.logging.Logger;
import java.util.logging.Level;

import org.hibernate.*;
import org.hibernate.cfg.*;
import org.hibernate.util.PropertiesHelper;


/**
 * Basic Hibernate helper class, handles SessionFactory, Session and Transaction.
 * <p>
 * Uses a static initializer to read startup options and initialize
 * <m_tt>Configuration</m_tt> and <m_tt>SessionFactory</m_tt>
 * <p>
 * This class tries to figure out if either ThreadLocal handling of the
 * <m_tt>Session</m_tt> and <m_tt>Transaction</m_tt> should be used, or if CMT is used.
 * In the latter case transaction/session handling methods are disabled and the
 * container does the job with Hibernate's automatic JTA binding. To keep your
 * DAOs free from any of this, just call <m_tt>HibernateUtil.getSession()</m_tt> in
 * the constructor of each DAO and use either client transactions/BMT or CMT
 * to set transaction and session boundaries.
 * <p>
 * If you want to assign a global interceptor, set its fully qualified
 * classname with the system (or hibernate.properties) property
 * <m_tt>hibernateutil.interceptor</m_tt>. It will be loaded and instantiated
 * on static initialization of HibernateUtil, and it has to have a
 * no-argument constructor. You can call <m_tt>getInterceptor()</m_tt> if
 * you need to provide settings before using the interceptor.
 *
 * @author christian@hibernate.org
 */
public class HibernateUtil 
{
    public static String HBM_XML_FILE = "hibernate.cfg.xml";

    /**
     * IMPORTANT - this is the only thing to ever need editing in this file 
     */
    protected static Configuration newConfiguration()
    {
        //
        // This assumes you've got a <CLASS>.hbm.xml file in the same dir
        // as your user class. If you decided to call your file something 
        // else, use Configuration.???("MyMappingFile.hbm.xml"). 
        //        
        Configuration cfg = new Configuration().configure(HBM_XML_FILE);

        cfg.addClass(com.gtfsdb.db.Agency.class);
        cfg.addClass(com.gtfsdb.db.Calendar.class);
        cfg.addClass(com.gtfsdb.db.CalendarDates.class);
        cfg.addClass(com.gtfsdb.db.FareAttributes.class);
        cfg.addClass(com.gtfsdb.db.FareRules.class);
        cfg.addClass(com.gtfsdb.db.Frequencies.class);
        cfg.addClass(com.gtfsdb.db.Patterns.class);
        cfg.addClass(com.gtfsdb.db.RouteType.class);
        cfg.addClass(com.gtfsdb.db.Routes.class);
        cfg.addClass(com.gtfsdb.db.StopTimes.class);
        cfg.addClass(com.gtfsdb.db.Stops.class);
        cfg.addClass(com.gtfsdb.db.Transfers.class);
        cfg.addClass(com.gtfsdb.db.Trips.class);
        cfg.addClass(com.gtfsdb.db.UniversalCalendar.class);

        return cfg;
    }


    private static final Logger LOGGER = Logger.getLogger(HibernateUtil.class.getCanonicalName());

    private static Configuration configuration;
    private static SessionFactory sessionFactory;
    private static ThreadLocal<Session>     threadSession     = new ThreadLocal<Session>();
    private static ThreadLocal<Transaction> threadTransaction = new ThreadLocal<Transaction>();

    private static boolean useJNDIBinding = false;
    private static boolean useThreadLocal = true;

   // Create the initial SessionFactory from the default configuration files
   static 
   {
      try 
      {
            // Replace with Configuration() if you don't use annotations
            configuration = newConfiguration();

            // Assign a global, user-defined interceptor with no-arg constructor
            String interceptorName = PropertiesHelper.getString("hibernateutil.interceptor_class",
                                                                configuration.getProperties(),
                                                                null);
            if (interceptorName != null) 
            {
                Class interceptorClass = HibernateUtil.class.getClassLoader().loadClass(interceptorName);
                Interceptor interceptor = (Interceptor)interceptorClass.newInstance();
                configuration.setInterceptor(interceptor);
            }

            // Enable JNDI binding code if the SessionFactory has a name
            if (configuration.getProperty(Environment.SESSION_FACTORY_NAME) != null)
                useJNDIBinding = true;
           
            // Disable ThreadLocal Session/Transaction handling if CMT is used
            if ("org.hibernate.transaction.CMTTransactionFactory"
                 .equals( configuration.getProperty(Environment.TRANSACTION_STRATEGY) ) )
                useThreadLocal = false;

            if (useJNDIBinding) {
                // Let Hibernate bind it to JNDI
                configuration.buildSessionFactory();
            } else {
                // or use static variable handling
                sessionFactory = configuration.buildSessionFactory();
            }

      } 
      catch (Throwable ex) 
      {
         // We have to catch Throwable, otherwise we will miss
         // NoClassDefFoundError and other subclasses of Error
          LOGGER.log(Level.SEVERE, "Building SessionFactory failed.", ex);
         throw new ExceptionInInitializerError(ex);
      }
   }

    /**
     * Returns the original Hibernate configuration.
     *
     * @return Configuration
     */
    public static Configuration getConfiguration() 
    {
        return configuration;
    }

   /**
    * Returns the SessionFactory used for this static class.
    *
    * @return SessionFactory
    */
   public static SessionFactory getSessionFactory() 
   {
      if (useJNDIBinding) {
            SessionFactory sessions = null;
            try {
                LOGGER.log(Level.INFO, "Looking up SessionFactory in JNDI.");
                javax.naming.Context ctx = new javax.naming.InitialContext();
                String jndiName = "java:hibernate/HibernateFactory";
                sessions = (SessionFactory)ctx.lookup(jndiName);
            } catch (javax.naming.NamingException ex) {
                throw new RuntimeException(ex);
            }
            return sessions;
        }
        if (sessionFactory == null)
            throw new IllegalStateException("Hibernate has been shut down.");

        return sessionFactory;
   }

    /**
     * Closes the current SessionFactory and releases all resources.
     * <p>
     * The only other method that can be called on HibernateUtil
     * after this one is rebuildSessionFactory(Configuration).
     * Note that this method should only be used with static SessionFactory
     * management, not with JNDI or any other external registry.
     */
    public static void shutdown() {
        LOGGER.log(Level.INFO, "Shutting down Hibernate.");
        // Close caches and connection pools
        getSessionFactory().close();

        // Clear static variables
        configuration = null;
        sessionFactory = null;

        // Clear ThreadLocal variables
        threadSession.set(null);
        threadTransaction.set(null);
    }


   /**
    * Rebuild the SessionFactory with the static Configuration.
    * <p>
     * This method also closes the old SessionFactory before, if still open.
     * Note that this method should only be used with static SessionFactory
     * management, not with JNDI or any other external registry.
    */
    public static void rebuildSessionFactory() {
        LOGGER.log(Level.INFO, "Using current Configuration for rebuild.");
        rebuildSessionFactory(configuration);
    }

   /**
    * Rebuild the SessionFactory with the given Hibernate Configuration.
    * <p>
     * HibernateUtil does not configure() the given Configuration object,
     * it directly calls buildSessionFactory(). This method also closes
     * the old SessionFactory before, if still open.
     *
    * @param cfg
    */
    public static void rebuildSessionFactory(Configuration cfg) {
        LOGGER.log(Level.INFO, "Rebuilding the SessionFactory from given Configuration.");
      synchronized(sessionFactory) {
            if (sessionFactory != null && !sessionFactory.isClosed())
                sessionFactory.close();
            if (useJNDIBinding)
                cfg.buildSessionFactory();
            else
                sessionFactory = cfg.buildSessionFactory();
            configuration = cfg;
      }
    }

   /**
    * Retrieves the current Session local to the thread.
    * <p/>
    * If no Session is open, opens a new Session for the running thread.
    *
    * @return Session
    */
   public static Session getSession() 
   {
       Session retVal = null;
        if (useThreadLocal) 
        {
            retVal = threadSession.get();
            if(retVal == null) 
            {
                LOGGER.log(Level.INFO, "Opening new Session for this thread.");
                retVal = getSessionFactory().openSession();
                threadSession.set(retVal);
            }
        }
        else 
        {
            retVal = getSessionFactory().getCurrentSession();
        }

        return retVal;
   }

   /**
    * Closes the Session local to the thread.
    */
   public static void closeSession() {
        if (useThreadLocal) {
            Session s = threadSession.get();
            threadSession.set(null);
            if (s != null && s.isOpen()) {
                LOGGER.log(Level.INFO, "Closing Session of this thread.");
                s.close();
            }
        } else {
            LOGGER.log(Level.INFO, "Using CMT/JTA, intercepted superfluous close call.");
        }
   }

   /**
    * Start a new database transaction.
    */
   public static void beginTransaction() {
        if (useThreadLocal) {
            Transaction tx = threadTransaction.get();
            if (tx == null) {
                LOGGER.log(Level.INFO, "Starting new database transaction in this thread.");
                tx = getSession().beginTransaction();
                threadTransaction.set(tx);
            }
        } else {
            LOGGER.log(Level.INFO, "Using CMT/JTA, intercepted superfluous tx begin call.");
        }
   }

   /**
    * Commit the database transaction.
    */
   public static void commitTransaction() {
        if (useThreadLocal) {
            Transaction tx = threadTransaction.get();
            try {
                if ( tx != null && !tx.wasCommitted()
                                && !tx.wasRolledBack() ) {
                    LOGGER.log(Level.INFO, "Committing database transaction of this thread.");
                    tx.commit();
                }
                threadTransaction.set(null);
            } catch (RuntimeException ex) {
                LOGGER.log(Level.SEVERE, "", ex);
                rollbackTransaction();
                throw ex;
            }
        } else {
            LOGGER.log(Level.INFO, "Using CMT/JTA, intercepted superfluous tx commit call.");
        }
   }

   /**
    * Rollback the database transaction.
    */
   public static void rollbackTransaction() {
        if (useThreadLocal) {
            Transaction tx = threadTransaction.get();
            try {
                threadTransaction.set(null);
                if ( tx != null && !tx.wasCommitted() && !tx.wasRolledBack() ) {
                    LOGGER.log(Level.INFO, "Tyring to rollback database transaction of this thread.");
                    tx.rollback();
                    LOGGER.log(Level.INFO, "Database transaction rolled back.");
                }
            } catch (RuntimeException ex) {
                throw new RuntimeException("Might swallow original cause, check ERROR log!", ex);
            } finally {
                closeSession();
            }
        } else {
            LOGGER.log(Level.INFO, "Using CMT/JTA, intercepted superfluous tx rollback call.");
        }
   }

   /**
    * Disconnect and return Session from current Thread.
    *
    * @return Session the disconnected Session
    */
   public static Session disconnectSession() {
        if (useThreadLocal) {
            Session session = getSession();
            threadSession.set(null);
            if (session.isConnected() && session.isOpen()) {
                LOGGER.log(Level.INFO, "Disconnecting Session from this thread.");
                session.disconnect();
            }
            return session;
        } else {
            LOGGER.log(Level.INFO, "Using CMT/JTA, intercepted not supported disconnect call.");
            return null;
        }
   }

   /**
    * Register a Hibernate interceptor with the current SessionFactory.
    * <p>
    * Every Session opened is opened with this interceptor after
    * registration. Has no effect if the current Session of the
    * thread is already open, effective on next close()/getSession().
     * <p>
     * Attention: This method effectively restarts Hibernate. If you
     * need an interceptor active on static startup of HibernateUtil, set
     * the <m_tt>hibernateutil.interceptor</m_tt> system property to its
     * fully qualified class name.
    */
   public static void registerInterceptorAndRebuild(Interceptor interceptor) {
        LOGGER.log(Level.INFO, "Setting new global Hibernate interceptor and restarting.");
      configuration.setInterceptor(interceptor);
        rebuildSessionFactory();
   }

   public static Interceptor getInterceptor() {
        return configuration.getInterceptor();
   }

} 
